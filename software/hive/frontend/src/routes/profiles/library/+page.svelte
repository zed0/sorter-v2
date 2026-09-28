<script lang="ts">
	import { api, type SortingProfileSummary } from '$lib/api';
	import Spinner from '$lib/components/Spinner.svelte';
	import ProfileCard from '$lib/components/profile/ProfileCard.svelte';

	let profiles = $state<SortingProfileSummary[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let removingId = $state<string | null>(null);

	$effect(() => {
		loadProfiles();
	});

	async function loadProfiles() {
		loading = true;
		error = null;
		try {
			profiles = await api.getProfiles({ scope: 'library' });
		} catch (e: any) {
			error = e.error || 'Failed to load your library';
		} finally {
			loading = false;
		}
	}

	async function removeFromLibrary(profile: SortingProfileSummary) {
		removingId = profile.id;
		error = null;
		try {
			await api.removeSortingProfileFromLibrary(profile.id);
			profiles = profiles.filter((p) => p.id !== profile.id);
		} catch (e: any) {
			error = e.error || 'Failed to remove profile from library';
		} finally {
			removingId = null;
		}
	}
</script>

<svelte:head>
	<title>My Library - Hive</title>
</svelte:head>

<div class="mb-6 flex flex-wrap items-start justify-between gap-4">
	<div>
		<a href="/profiles" class="text-sm text-primary hover:text-primary-hover">&larr; My Profiles</a>
		<h1 class="mt-2 text-2xl font-bold text-text">My Library</h1>
		<p class="mt-1 text-sm text-text-muted">
			Profiles you've saved. Saved profiles can be assigned to your machines.
		</p>
	</div>
	<a
		href="/profiles/discover"
		class="border border-border px-4 py-2 text-sm font-medium text-text hover:bg-bg"
	>
		Browse Public Profiles
	</a>
</div>

{#if error}
	<div class="mb-4 bg-primary/8 p-3 text-sm text-primary">{error}</div>
{/if}

{#if loading}
	<div class="flex justify-center p-8"><Spinner size={32} /></div>
{:else if profiles.length === 0}
	<div class="border border-border bg-surface p-6 text-sm text-text-muted">
		Your library is empty. <a href="/profiles/discover" class="text-primary hover:text-primary-hover">Browse public profiles</a> and save the ones you want to use.
	</div>
{:else}
	<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
		{#each profiles as profile (profile.id)}
			<ProfileCard {profile} onremove={removeFromLibrary} removing={removingId === profile.id} />
		{/each}
	</div>
{/if}
