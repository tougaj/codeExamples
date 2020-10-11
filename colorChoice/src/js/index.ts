(function main() {
	let tm: number | null = null;

	function fillColorTable(container: HTMLDivElement) {
		function addColorItem(color: string) {
			const div = document.createElement('div');
			div.className = 'color-box';
			div.style.backgroundColor = color;
			div.dataset.color = color;
			div.addEventListener('click', function () {
				(document.querySelector('.selected-color') as HTMLDivElement).style.backgroundColor =
					this.dataset.color || 'transparent';
				this.closest('.color-table')?.classList.remove('active');
				if (tm) clearTimeout(tm);
			});

			container?.appendChild(div);
		}

		for (let i = 0; i < 0b1000; i++) {
			let color = i.toString(2).replace(/1/g, 'f');
			color = `#${(color as any).padStart(3, '0')}`;
			addColorItem(color);
		}
	}

	function toggleColorTable(this: Element) {
		const colorTable = this.nextElementSibling;
		colorTable?.classList.toggle('active');
		tm = setTimeout(() => {
			colorTable?.classList.remove('active');
			tm = null;
		}, 5000);
	}

	const addColorTable = (anchorElement: HTMLAnchorElement | null) => {
		if (!anchorElement) return;
		const colorTable = document.createElement('div');
		colorTable.className = 'color-table';
		fillColorTable(colorTable);
		anchorElement.parentElement?.appendChild(colorTable);
		anchorElement.addEventListener('click', toggleColorTable);
	};

	document.addEventListener('DOMContentLoaded', () => {
		addColorTable(document.querySelector('#aForeColor'));
	});
})();
