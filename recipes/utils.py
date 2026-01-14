from io import BytesIO
import base64
import matplotlib.pyplot as plt


def get_graph(fig):
    """Encode the matplotlib figure as base64 PNG."""
    buffer = BytesIO()

    # IMPORTANT:
    # Do NOT use bbox_inches="tight" (it expands pie charts!)
    fig.savefig(buffer, format="png", dpi=100, facecolor=fig.get_facecolor())

    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode("utf-8")
    buffer.close()
    plt.close(fig)
    return graph


def style_axes(fig, ax):
    """Apply dark transparent theme."""

    # Transparent dark grey background
    fig.patch.set_facecolor((0.1, 0.1, 0.1, 0.7))
    ax.set_facecolor((0.1, 0.1, 0.1, 0.4))

    # White axis text
    ax.tick_params(colors="white")

    # White spines
    for spine in ax.spines.values():
        spine.set_color("white")

    # White labels/titles
    ax.title.set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")


def get_chart(chart_type, data=None, **kwargs):
    """Generate chart based on type and data, return as base64 PNG."""

    plt.switch_backend("AGG")

    # 🚀 Fixed size for ALL charts → SAME PNG dimensions
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

    # Apply theme
    style_axes(fig, ax)

    # BAR -----------------------------------------------------------
    if chart_type == "bar" and data is not None:
        ax.bar(data["difficulty"], data["AvgCookingTime"], color="#CBE58B")
        ax.set_xlabel("Difficulty")
        ax.set_ylabel("Average Cooking Time (minutes)")
        ax.set_title("Average Cooking Time by Difficulty")

    # PIE -----------------------------------------------------------
    elif chart_type == "pie":
        labels = kwargs.get("labels")
        sizes = kwargs.get("sizes")

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%"
        )

        # All pie texts readable
        for t in texts:
            t.set_color("white")
        for t in autotexts:
            t.set_color("white")

        ax.set_title("Difficulty Distribution")

        ax.set_aspect("equal")  # perfect circle

    # LINE ----------------------------------------------------------
    elif chart_type == "line" and data is not None:
        ax.plot(data["cooking_time"], data["CumulativeCount"], color="#CBE58B")
        ax.set_xlabel("Cooking Time (minutes)")
        ax.set_ylabel("Cumulative Recipe Count")
        ax.set_title("Cumulative Recipes by Cooking Time")

    else:
        raise ValueError("Unknown chart type or missing data.")

    fig.tight_layout()
    return get_graph(fig)
