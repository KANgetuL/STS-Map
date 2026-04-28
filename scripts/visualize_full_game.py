import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sts_map.api.generate_map import generate_map
from sts_map.domain.models import GenerationInput
from sts_map.domain.enums import ActId, RoomType

# Character mapping corresponding to doc/UI.md
CHAR_MAP = {
    RoomType.MONSTER: '+',
    RoomType.ELITE: '#',
    RoomType.QUESTION: '?',
    RoomType.EVENT: '?',
    RoomType.SHOP: '$',
    RoomType.REST: '=',
    RoomType.BOSS: '@',
    RoomType.TREASURE: '!',  # Boss Chest proxy
    RoomType.SPECIAL_ELITE: '#',
}

def get_node_char(floor: int, max_floor: int, room_type: RoomType) -> str:
    """Determine character representation for a node."""
    if floor == 0:
        return 'S'  # Start node
    if floor == max_floor:
        return '@'  # Boss node
    return CHAR_MAP.get(room_type, '?')

def visualize_full_game(seed: int = 42, ascension: int = 1, rule_version: str = "v1"):
    acts = [ActId.ACT1, ActId.ACT2, ActId.ACT3, ActId.ACT4]
    
    # Create matplotlib setup with a parchment background color
    parchment_color = "#f4f1e1"
    fig, ax = plt.subplots(figsize=(8, 24), facecolor=parchment_color)
    ax.set_facecolor(parchment_color)
    
    current_y_offset = 0
    y_spacing = 1.0
    x_spacing = 1.0
    
    all_xy = []

    for act in acts:
        # Generate the graph for this act
        input_data = GenerationInput(act_id=act, ascension=ascension, seed=seed, rule_version=rule_version)
        try:
            graph = generate_map(input_data)
        except Exception as e:
            print(f"Skipping {act} due to generation error: {e}")
            continue
            
        nodes_by_floor = graph.nodes_by_floor
        if not nodes_by_floor:
            continue
            
        max_floor = max(nodes_by_floor.keys())
        
        # Draw edges first so they sit properly underneath text/nodes
        for edge in graph.edges:
            src_x = edge.src.x * x_spacing
            src_y = edge.src.floor * y_spacing + current_y_offset
            
            dst_x = edge.dst.x * x_spacing
            dst_y = edge.dst.floor * y_spacing + current_y_offset
            
            ax.plot([src_x, dst_x], [src_y, dst_y], color="#8b7b62", linewidth=1.5, zorder=1, alpha=0.6)

        # Draw nodes with corresponding text
        for floor, nodes in nodes_by_floor.items():
            for node in nodes:
                x = node.id.x * x_spacing
                y = floor * y_spacing + current_y_offset
                all_xy.append((x, y))
                
                char = get_node_char(floor, max_floor, node.display_type)
                
                # Draw small circle background for the text
                circle = patches.Circle((x, y), radius=0.25, color=parchment_color, ec="#8b7b62", zorder=2)
                ax.add_patch(circle)
                
                # Plot the symbol
                ax.text(x, y, char, ha='center', va='center', 
                        fontsize=12, fontweight='bold', color="#4a3e35", zorder=3, family='monospace')
        
        # Add visual separation + title between Acts
        ax.text(3, current_y_offset - 1.5, f"--- {act.value.upper()} ---", ha='center', va='center',
                fontsize=16, fontweight='bold', color="#4a3e35", zorder=3)
                
        # Move up offset for next act, with a 3-floor gap
        current_y_offset += (max_floor + 4) * y_spacing

    if not all_xy:
        print("No maps generated.")
        return

    # Auto-adjust limits to fit everything neatly
    xs = [pt[0] for pt in all_xy]
    ys = [pt[1] for pt in all_xy]
    ax.set_xlim(min(xs) - 1, max(xs) + 1)
    ax.set_ylim(min(ys) - 3, max(ys) + 1)
    
    # Hide axes for cleaner aesthetics
    ax.axis("off")
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "full_sts_map.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=parchment_color)
    print(f"Map successfully generated and saved to {output_path}")

if __name__ == "__main__":
    visualize_full_game(rule_version="0.6.0")
