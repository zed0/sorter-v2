<script lang="ts">
	import { onMount } from 'svelte';
	import { getBackendHttpBase, machineHttpBaseUrlFromWsUrl } from '$lib/backend';
	import { getMachineContext } from '$lib/machines/context';
	import Switch from '$lib/components/ui/Switch.svelte';
	import SettingRow from '$lib/components/ui/SettingRow.svelte';

	const machine = getMachineContext();

	const DEFAULT_ENABLED = false;

	let enabled = $state(DEFAULT_ENABLED);
	let loading = $state(true);
	let saving = $state(false);
	let errorMsg = $state<string | null>(null);

	function currentBackendBaseUrl(): string {
		return machineHttpBaseUrlFromWsUrl(machine.machine?.url) ?? getBackendHttpBase();
	}

	async function loadConfig() {
		loading = true;
		try {
			const res = await fetch(`${currentBackendBaseUrl()}/api/system/dashboard-config`);
			if (!res.ok) throw new Error(await res.text());
			const payload = await res.json();
			enabled = Boolean(payload?.debug_incidents);
			errorMsg = null;
		} catch (e: any) {
			errorMsg = e?.message ?? 'Failed to load incident debug config.';
		} finally {
			loading = false;
		}
	}

	async function saveEnabled(next: boolean) {
		saving = true;
		errorMsg = null;
		try {
			const res = await fetch(`${currentBackendBaseUrl()}/api/system/dashboard-config`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ debug_incidents: next })
			});
			if (!res.ok) throw new Error(await res.text());
			const payload = await res.json();
			enabled = Boolean(payload?.debug_incidents);
		} catch (e: any) {
			errorMsg = e?.message ?? 'Failed to update incident debug config.';
		} finally {
			saving = false;
		}
	}

	onMount(() => {
		void loadConfig();
	});
</script>

<div class="divide-y divide-line">
	<SettingRow
		label="Debug capture on incidents"
		help="When a new incident fires, save a JPEG from every camera plus the current classification-channel piece list, and another camera round once it resolves, attached to that incident's record for later review. Takes effect immediately, no restart needed. Off by default (extra per-incident camera work)."
		changed={enabled !== DEFAULT_ENABLED}
		defaultText={DEFAULT_ENABLED ? 'on' : 'off'}
		onreset={() => saveEnabled(DEFAULT_ENABLED)}
	>
		<Switch
			checked={enabled}
			label="Debug capture on incidents"
			disabled={loading || saving}
			onchange={(on) => saveEnabled(on)}
		/>
	</SettingRow>

	{#if errorMsg}
		<p class="px-(--pad-panel) py-(--pad-row) text-sm text-danger-ink">{errorMsg}</p>
	{/if}
</div>
