<script lang="ts">
	import { goto } from '$app/navigation';
	import { api, type SortingProfileSummary } from '$lib/api';
	import Spinner from '$lib/components/Spinner.svelte';
	import ProfileCard from '$lib/components/profile/ProfileCard.svelte';

	let profiles = $state<SortingProfileSummary[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let busyProfileId = $state<string | null>(null);
	let creating = $state(false);
	let deleteTarget = $state<SortingProfileSummary | null>(null);
	let deleting = $state(false);

	async function createProfile() {
		creating = true;
		error = null;
		try {
			const profile = await api.createSortingProfile({ name: 'Untitled Profile', visibility: 'private' });
			goto(`/profiles/${profile.id}/edit?new=1`);
		} catch (e: any) {
			error = e.error || 'Failed to create profile';
			creating = false;
		}
	}

	const scope = 'mine' as const;

	$effect(() => {
		loadProfiles();
	});

	async function loadProfiles() {
		loading = true;
		error = null;
		try {
			profiles = await api.getProfiles({ scope });
		} catch (e: any) {
			error = e.error || 'Failed to load sorting profiles';
		} finally {
			loading = false;
		}
	}

	async function confirmDelete() {
		if (!deleteTarget) return;
		deleting = true;
		error = null;
		try {
			await api.deleteSortingProfile(deleteTarget.id);
			profiles = profiles.filter(p => p.id !== deleteTarget!.id);
			deleteTarget = null;
		} catch (e: any) {
			error = e.error || 'Failed to delete profile';
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>Profiles - Hive</title>
</svelte:head>

<div class="mb-6 flex flex-wrap items-start justify-between gap-4">
	<div>
		<h1 class="text-2xl font-bold text-text">Sorting Profiles</h1>
		<p class="mt-1 text-sm text-text-muted">
			Build, share, fork, and assign sorting logic across your machines.
		</p>
	</div>
	<div class="flex flex-wrap gap-2">
		<a
			href="/profiles/discover"
			class="border border-border px-4 py-2 text-sm font-medium text-text hover:bg-bg"
		>
			Browse Public Profiles
		</a>
		<button
			onclick={createProfile}
			disabled={creating}
			class="bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-hover disabled:opacity-50"
		>
			{creating ? 'Creating...' : 'New Profile'}
		</button>
	</div>
</div>


{#if error}
	<div class="mb-4 bg-primary/8 p-3 text-sm text-primary">{error}</div>
{/if}

{#if loading}
	<div class="flex justify-center p-8"><Spinner size={32} /></div>
{:else if profiles.length === 0}
	<div class="border border-border bg-surface p-6 text-sm text-text-muted">You have not created any profiles yet.</div>
{:else}
	<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
		{#each profiles as profile (profile.id)}
			<ProfileCard {profile} ondelete={(p) => { deleteTarget = p; }} />
		{/each}
	</div>
{/if}

{#if deleteTarget}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onkeydown={(e) => { if (e.key === 'Escape') deleteTarget = null; }} onclick={() => deleteTarget = null}>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="mx-4 w-full max-w-md bg-surface p-4 sm:p-6"
			role="dialog"
			aria-modal="true"
			tabindex="-1"
			onclick={(e) => e.stopPropagation()}
			onkeydown={(e) => e.stopPropagation()}
		>
			<h3 class="text-lg font-semibold text-text">Delete Profile</h3>
			<p class="mt-2 text-sm text-text-muted">
				Are you sure you want to delete <span class="font-medium text-text">{deleteTarget.name}</span>? This action cannot be undone.
			</p>
			{#if error}
				<div class="mt-3 bg-primary/8 p-2 text-sm text-primary">{error}</div>
			{/if}
			<div class="mt-6 flex justify-end gap-3">
				<button
					onclick={() => deleteTarget = null}
					disabled={deleting}
					class="border border-border bg-surface px-4 py-2 text-sm font-medium text-text-muted hover:bg-bg disabled:opacity-50"
				>Cancel</button>
				<button
					onclick={confirmDelete}
					disabled={deleting}
					class="bg-danger px-4 py-2 text-sm font-medium text-white hover:bg-primary-hover disabled:opacity-50"
				>{deleting ? 'Deleting...' : 'Delete'}</button>
			</div>
		</div>
	</div>
{/if}
