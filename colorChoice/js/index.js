"use strict";
(function main() {
    var tm = null;
    function fillColorTable(container) {
        function addColorItem(color) {
            var div = document.createElement('div');
            div.className = 'color-box';
            div.style.backgroundColor = color;
            div.dataset.color = color;
            div.addEventListener('click', function () {
                var _a;
                document.querySelector('.selected-color').style.backgroundColor =
                    this.dataset.color || 'transparent';
                (_a = this.closest('.color-table')) === null || _a === void 0 ? void 0 : _a.classList.remove('active');
                if (tm)
                    clearTimeout(tm);
            });
            container === null || container === void 0 ? void 0 : container.appendChild(div);
        }
        for (var i = 0; i < 8; i++) {
            var color = i.toString(2).replace(/1/g, 'f');
            color = "#" + color.padStart(3, '0');
            addColorItem(color);
        }
    }
    function toggleColorTable() {
        var colorTable = this.nextElementSibling;
        colorTable === null || colorTable === void 0 ? void 0 : colorTable.classList.toggle('active');
        tm = setTimeout(function () {
            colorTable === null || colorTable === void 0 ? void 0 : colorTable.classList.remove('active');
            tm = null;
        }, 5000);
    }
    var addColorTable = function (anchorElement) {
        var _a;
        if (!anchorElement)
            return;
        var colorTable = document.createElement('div');
        colorTable.className = 'color-table';
        fillColorTable(colorTable);
        (_a = anchorElement.parentElement) === null || _a === void 0 ? void 0 : _a.appendChild(colorTable);
        anchorElement.addEventListener('click', toggleColorTable);
    };
    document.addEventListener('DOMContentLoaded', function () {
        addColorTable(document.querySelector('#aForeColor'));
    });
})();
