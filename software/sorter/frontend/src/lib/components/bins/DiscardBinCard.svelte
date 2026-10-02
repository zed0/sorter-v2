<script lang="ts">
	import Badge from '$lib/components/ui/Badge.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import PartTile from '$lib/components/ui/PartTile.svelte';
	import type { DiscardContents, DiscardPiece } from './types';

	let { discard }: { discard: DiscardContents | null } = $props();

	const REASON_LABELS: Record<string, string> = {
		too_big: 'Oversized',
		too_big_for_layer: 'Too big for layer',
		multi_drop: 'Multi-drop',
		id_request_failed: 'ID request failed',
		unidentified: 'Unidentified',
		no_bin_for_category: 'No bin for category'
	};

	function reasonLabel(piece: DiscardPiece): string {
		const reason = piece.discard_reason;
		if (reason && REASON_LABELS[reason]) return REASON_LABELS[reason];
		if (reason) return reason.replace(/_/g, ' ');
		return 'Discarded';
	}

	function dataImageUrl(payload: string | null | undefined): string | null {
		return payload ? `data:image/jpeg;base64,${payload}` : null;
	}

	function pieceImage(piece: DiscardPiece): string | null {
		// A piece that short-circuited straight to a terminal status without
		// ever running the burst-capture/classify pipeline (multi-drop is the
		// main case) never gets top/bottom/thumbnail: latest_captured_crop
		// (the live per-frame tracking crop) is the only real photo of it.
		// brickognize_preview_url is a stock reference image, not a photo of
		// this piece, so it's the last resort.
		return (
			dataImageUrl(piece.top_image) ??
			dataImageUrl(piece.bottom_image) ??
			dataImageUrl(piece.thumbnail) ??
			dataImageUrl(piece.latest_captured_crop) ??
			piece.brickognize_preview_url ??
			null
		);
	}
</script>

<!-- The virtual passthrough "bin": pieces without a matching rule fall through
     every layer's doors into the discard bucket below the machine. It is shown
     so the operator knows the output exists; it is not interactive and has no
     physical slot. -->
<Panel title="Discard bin">
	{#snippet actions()}<Badge>Virtual</Badge>{/snippet}
	<p class="text-sm text-ink-muted">
		Pieces that match no sorting rule, or whose category has no assigned bin, fall through all layer
		doors into the discard bucket below the machine. Empty it by hand when it fills up.
	</p>

	{#if discard && discard.count > 0}
		<p class="mt-4 text-sm text-ink">
			<span class="num font-medium">{discard.count}</span>
			piece{discard.count === 1 ? '' : 's'} discarded this session{#if discard.recent_pieces.length < discard.count}<span
					class="text-ink-muted"
				>
					· the most recent {discard.recent_pieces.length}</span
				>{/if}
		</p>
		<div class="mt-3 grid grid-cols-[repeat(auto-fill,minmax(7rem,1fr))] gap-4">
			{#each discard.recent_pieces as piece (piece.uuid)}
				<PartTile
					layout="tile"
					name={reasonLabel(piece)}
					imgUrl={pieceImage(piece)}
					bricklinkId={piece.part_id ?? piece.category_id ?? null}
				/>
			{/each}
		</div>
	{/if}
</Panel>
