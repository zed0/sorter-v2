<script lang="ts">
	import { api, type SortingProfileSummary } from '$lib/api';
	import Spinner from '$lib/components/Spinner.svelte';
	import ProfileCard from '$lib/components/profile/ProfileCard.svelte';

	let profiles = $state<SortingProfileSummary[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let search = $state('');

	const filtered = $derived.by(() => {
		const needle = search.trim().toLowerCase();
		if (!needle) return profiles;
		return profiles.filter(
			(p) => p.name.toLowerCase().includes(needle) || (p.description ?? '').toLowerCase().includes(needle)
		);
	});

	$effect(() => {
		loadProfiles();
	});

	async function loadProfiles() {
		loading = true;
		error = null;
		try {
			profiles = await api.getProfiles({ scope: 'discover', sort: 'library' });
		} catch (e: any) {
			error = e.error || 'Failed to load public profiles';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Public Profiles - Hive</title>
</svelte:head>

<div class="mb-6">
	<a href="/profiles" class="text-sm text-primary hover:text-primary-hover">&larr; My Profiles</a>
	<h1 class="mt-2 text-2xl font-bold text-text">Public Profiles</h1>
	<p class="mt-1 text-sm text-text-muted">
		Published sorting profiles shared by the community, most saved first.
	</p>
</div>

<div class="mb-4">
	<input
		type="search"
		bind:value={search}
		placeholder="Search by name or description"
		aria-label="Search public profiles"
		class="w-full max-w-md border border-border bg-surface px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
	/>
</div>

{#if error}
	<div class="mb-4 bg-primary/8 p-3 text-sm text-primary">{error}</div>
{/if}

{#if loading}
	<div class="flex justify-center p-8"><Spinner size={32} /></div>
{:else if profiles.length === 0}
	<div class="border border-border bg-surface p-6 text-sm text-text-muted">No public profiles have been published yet.</div>
{:else if filtered.length === 0}
	<div class="border border-border bg-surface p-6 text-sm text-text-muted">No public profiles match "{search.trim()}".</div>
{:else}
	<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
		{#each filtered as profile (profile.id)}
			<ProfileCard {profile} />
		{/each}
	</div>
{/if}
