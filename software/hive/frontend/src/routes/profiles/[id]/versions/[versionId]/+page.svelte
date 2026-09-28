<script lang="ts">
	import { page } from '$app/state';
	import { api, type SortingProfileDetail } from '$lib/api';
	import Spinner from '$lib/components/Spinner.svelte';
	import RuleTreeView from '$lib/components/profile/RuleTreeView.svelte';

	let loading = $state(true);
	let profile = $state<SortingProfileDetail | null>(null);
	let error = $state<string | null>(null);

	const profileId = $derived(page.params.id ?? '');
	const versionId = $derived(page.params.versionId ?? '');
	const version = $derived(profile?.current_version ?? null);

	// versions come newest first; neighbours are only the ones this viewer may see.
	const versionIndex = $derived(profile ? profile.versions.findIndex((v) => v.id === versionId) : -1);
	const newer = $derived(profile && versionIndex > 0 ? profile.versions[versionIndex - 1] : null);
	const older = $derived(
		profile && versionIndex >= 0 && versionIndex < profile.versions.length - 1 ? profile.versions[versionIndex + 1] : null
	);

	const defaultCategoryName = $derived(
		version ? (version.categories?.[version.default_category_id]?.name ?? version.default_category_id) : ''
	);

	$effect(() => {
		if (profileId && versionId) void load(profileId, versionId);
	});

	async function load(id: string, vid: string) {
		loading = true;
		error = null;
		try {
			profile = await api.getSortingProfile(id, vid);
		} catch (e: any) {
			profile = null;
			error = e.error || 'Failed to load version';
		} finally {
			loading = false;
		}
	}

	function coveragePct(v: number | null | undefined): string {
		return v == null ? 'n/a' : `${(v * 100).toFixed(1)}%`;
	}
</script>

<svelte:head>
	<title>{profile && version ? `${profile.name} v${version.version_number} - Hive` : 'Profile Version - Hive'}</title>
</svelte:head>

{#if loading}
	<div class="flex justify-center p-8"><Spinner size={32} /></div>
{:else if !profile || !version}
	<div class="space-y-3">
		<a href={`/profiles/${profileId}`} class="text-sm text-primary hover:text-primary-hover">&larr; Back to profile</a>
		<div class="border border-primary/20 bg-primary-light p-4 text-sm text-primary">{error ?? 'Version not found.'}</div>
	</div>
{:else}
	<div class="space-y-6">
		<div>
			<a href={`/profiles/${profile.id}`} class="text-sm text-primary hover:text-primary-hover">&larr; {profile.name}</a>
			<div class="mt-2 flex flex-wrap items-center gap-2">
				<h1 class="text-2xl font-bold text-text">{profile.name} <span class="text-text-muted">v{version.version_number}</span></h1>
				{#if version.is_published}
					<span class="border border-success/20 bg-success/[0.08] px-2 py-0.5 text-xs font-medium text-success">Published</span>
				{:else}
					<span class="border border-border bg-bg px-2 py-0.5 text-xs font-medium text-text-muted">Draft</span>
				{/if}
				{#if version.label}<span class="border border-border bg-bg px-2 py-0.5 text-xs font-medium text-text-muted">{version.label}</span>{/if}
				<span class="border border-border bg-bg px-2 py-0.5 text-xs font-medium text-text-muted">Read-only</span>
			</div>
			{#if version.change_note}<p class="mt-1 text-sm text-text-muted">{version.change_note}</p>{/if}
			<p class="mt-1 text-xs text-text-muted">
				Saved {new Date(version.created_at).toLocaleString()} · {version.compiled_part_count} parts · {coveragePct(version.coverage_ratio)} coverage · fallback category: {defaultCategoryName}
			</p>
		</div>

		<div class="flex flex-wrap items-center justify-between gap-2">
			<div class="flex flex-wrap gap-2">
				{#if older}
					<a href={`/profiles/${profile.id}/versions/${older.id}`} class="border border-border px-3 py-1.5 text-sm font-medium text-text hover:bg-bg">&larr; v{older.version_number}</a>
				{/if}
				{#if newer}
					<a href={`/profiles/${profile.id}/versions/${newer.id}`} class="border border-border px-3 py-1.5 text-sm font-medium text-text hover:bg-bg">v{newer.version_number} &rarr;</a>
				{/if}
			</div>
			{#if profile.is_owner}
				<a href={`/profiles/${profile.id}/edit`} class="bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-hover">Edit Profile</a>
			{/if}
		</div>

		<div class="border border-border bg-surface p-6">
			<h2 class="mb-4 text-lg font-semibold text-text">Rules</h2>
			{#if version.rules.length === 0}
				<p class="text-sm text-text-muted">This version has no rules.</p>
			{:else}
				<RuleTreeView rules={version.rules} />
			{/if}
		</div>
	</div>
{/if}
