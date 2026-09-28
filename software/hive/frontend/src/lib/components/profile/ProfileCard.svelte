<script lang="ts">
	import type { SortingProfileSummary } from '$lib/api';
	import EyeOff from 'lucide-svelte/icons/eye-off';
	import Trash2 from 'lucide-svelte/icons/trash-2';

	interface Props {
		profile: SortingProfileSummary;
		/** Shown as a delete button on owned profiles when provided. */
		ondelete?: (profile: SortingProfileSummary) => void;
	}

	let { profile, ondelete }: Props = $props();

	const rules = $derived(profile.latest_version?.rules_summary ?? []);
	const activeRules = $derived(rules.filter((r) => !r.disabled));
</script>

<a href={profile.is_owner ? `/profiles/${profile.id}/edit` : `/profiles/${profile.id}`}
	class="group flex flex-col border border-border bg-surface transition-colors hover:border-text-muted">
	<!-- Header -->
	<div class="px-4 pt-4 pb-3">
		<div class="flex items-start justify-between gap-2">
			<div class="min-w-0">
				<h2 class="flex items-center gap-2 truncate text-sm font-semibold {profile.visibility === 'public' ? 'text-info' : 'text-text'}">
					{#if profile.visibility === 'public'}
						<span class="inline-block h-2.5 w-2.5 shrink-0 bg-info"></span>
					{:else}
						<span class="inline-block h-2.5 w-2.5 shrink-0 bg-text-muted"></span>
					{/if}
					{profile.name}
				</h2>
				{#if profile.description}
					<p class="mt-0.5 truncate text-xs text-text-muted">{profile.description}</p>
				{/if}
			</div>
			<div class="flex shrink-0 items-center gap-1.5">
				{#if profile.source}
					<span class="border border-warning/30 bg-warning/[0.1] px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-warning-strong">Fork</span>
				{/if}
				<span class="border border-border bg-bg px-1.5 py-0.5 text-[10px] font-medium text-text-muted">v{profile.latest_version_number}</span>
			</div>
		</div>
	</div>

	<!-- Rules list -->
	{#if activeRules.length > 0}
		<div class="border-t border-border px-4 py-2.5">
			<div class="space-y-1.5">
				{#each activeRules.slice(0, 6) as rule}
					<div class="flex items-center gap-2 text-xs">
						{#if rule.rule_type === 'set' && rule.set_meta?.img_url}
							<img src={rule.set_meta.img_url} alt="" class="h-5 w-5 shrink-0 object-contain" />
						{:else}
							<EyeOff size={14} class="shrink-0 text-text-muted" />
						{/if}
						<span class="truncate text-text">{rule.name}</span>
						{#if rule.rule_type === 'set' && rule.set_num}
							<span class="shrink-0 font-mono text-[10px] text-text-muted">{rule.set_num}</span>
						{:else if rule.condition_count > 0}
							<span class="shrink-0 text-[10px] text-text-muted">{rule.condition_count} cond{rule.condition_count !== 1 ? 's' : ''}</span>
						{/if}
						{#if rule.child_count > 0}
							<span class="shrink-0 text-[10px] text-text-muted">+{rule.child_count} sub</span>
						{/if}
					</div>
				{/each}
				{#if activeRules.length > 6}
					<div class="text-[10px] text-text-muted">+{activeRules.length - 6} more rules</div>
				{/if}
			</div>
		</div>
	{:else if rules.length === 0}
		<div class="border-t border-border px-4 py-2.5">
			<span class="text-xs text-text-muted">No rules defined</span>
		</div>
	{/if}

	<!-- Footer -->
	<div class="mt-auto border-t border-border bg-bg px-4 py-2">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2 text-[10px] text-text-muted">
				<span>{profile.latest_version?.compiled_part_count ?? 0} parts</span>
				{#if profile.library_count > 0}
					<span class="text-border">|</span>
					<span>{profile.library_count} {profile.library_count === 1 ? 'save' : 'saves'}</span>
				{/if}
				{#if profile.fork_count > 0}
					<span class="text-border">|</span>
					<span>{profile.fork_count} forks</span>
				{/if}
				{#if !profile.is_owner}
					<span class="text-border">|</span>
					<span>by {profile.owner.display_name ?? profile.owner.github_login ?? '?'}</span>
				{/if}
			</div>
			<div class="flex items-center gap-2">
				{#if profile.tags.length > 0}
					<div class="flex gap-1">
						{#each profile.tags.slice(0, 3) as tag}
							<span class="border border-border bg-bg px-1.5 py-0.5 text-[10px] text-text-muted">{tag}</span>
						{/each}
					</div>
				{/if}
				{#if profile.is_owner && ondelete}
					<button
						onclick={(e) => { e.preventDefault(); e.stopPropagation(); ondelete(profile); }}
						class="p-1 text-text-muted opacity-0 transition-opacity hover:text-primary group-hover:opacity-100 focus-visible:opacity-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
						title="Delete profile"
					>
						<Trash2 size={14} />
					</button>
				{/if}
			</div>
		</div>
	</div>
</a>
