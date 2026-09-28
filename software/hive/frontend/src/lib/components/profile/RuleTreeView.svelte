<script lang="ts">
	import type { CustomSetPart, SortingProfileRule } from '$lib/api';
	import RuleTreeView from './RuleTreeView.svelte';

	interface Props {
		rules: SortingProfileRule[];
		depth?: number;
	}

	let { rules, depth = 0 }: Props = $props();

	const ANY_COLOR_ID = -1;
	const opLabels: Record<string, string> = {
		eq: '=', neq: '!=', in: 'in', contains: 'contains',
		regex: 'regex', gte: '>=', lte: '<='
	};

	function formatValue(value: unknown): string {
		if (typeof value === 'string') return value;
		if (typeof value === 'number' || typeof value === 'boolean') return String(value);
		if (value === null || value === undefined) return '';
		return JSON.stringify(value);
	}

	function partColor(part: CustomSetPart): string {
		if (Number(part.color_id) === ANY_COLOR_ID) return 'Any color';
		return part.color_name ?? `Color ${part.color_id}`;
	}

	function ruleKind(rule: SortingProfileRule): string {
		if (rule.rule_type !== 'set') return 'Rule';
		return rule.set_source === 'custom' ? 'Custom set' : 'Set';
	}
</script>

<div class="space-y-2">
	{#each rules as rule (rule.id)}
		<div class="border border-border {depth === 0 ? 'bg-surface' : 'bg-bg'} p-3 {rule.disabled ? 'opacity-60' : ''}">
			<div class="flex flex-wrap items-center gap-2">
				{#if rule.rule_type === 'set' && rule.set_meta?.img_url}
					<img src={rule.set_meta.img_url} alt="" class="h-8 w-8 shrink-0 object-contain" />
				{/if}
				<span class="text-sm font-semibold text-text">{rule.name}</span>
				<span class="border border-border bg-bg px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-text-muted">{ruleKind(rule)}</span>
				{#if rule.disabled}
					<span class="border border-border bg-bg px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-text-muted">Disabled</span>
				{/if}
			</div>

			{#if rule.rule_type === 'set'}
				<div class="mt-2 text-xs text-text-muted">
					{#if rule.set_source !== 'custom'}
						<span class="font-mono">{rule.set_num}</span>
						{#if rule.set_meta?.year} · {rule.set_meta.year}{/if}
						{#if rule.set_meta?.num_parts} · {rule.set_meta.num_parts} parts{/if}
					{/if}
					{#if rule.include_spares} · includes spares{/if}
				</div>
				{#if rule.set_source === 'custom' && rule.custom_parts?.length}
					<ul class="mt-2 space-y-1 text-xs">
						{#each rule.custom_parts as part}
							<li class="flex flex-wrap items-center gap-2">
								<span class="font-mono text-text">{part.part_num}</span>
								{#if part.part_name}<span class="text-text-muted">{part.part_name}</span>{/if}
								<span class="text-text-muted">· {partColor(part)} · ×{part.quantity}</span>
							</li>
						{/each}
					</ul>
				{/if}
			{:else if rule.conditions.length > 0}
				<div class="mt-2 text-xs text-text-muted">
					Match {rule.match_mode === 'any' ? 'any' : 'all'} of:
				</div>
				<ul class="mt-1 space-y-1">
					{#each rule.conditions as condition (condition.id)}
						<li class="flex flex-wrap items-baseline gap-1.5 font-mono text-xs">
							<span class="text-text">{condition.field}</span>
							<span class="text-text-muted">{opLabels[condition.op] ?? condition.op}</span>
							<span class="break-all text-text">{formatValue(condition.value)}</span>
						</li>
					{/each}
				</ul>
			{:else}
				<div class="mt-2 text-xs text-text-muted">No conditions</div>
			{/if}

			{#if rule.children.length > 0}
				<div class="mt-3 pl-4">
					<RuleTreeView rules={rule.children} depth={depth + 1} />
				</div>
			{/if}
		</div>
	{/each}
</div>
