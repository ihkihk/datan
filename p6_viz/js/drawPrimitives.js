"use strict";

function drawTextButton(view, parent, x, y, w, h, txt, cls, callback, rx=20, ry=30) {
	var btn1 = parent.append('g').attr('class', cls).
		attr('transform', 'translate(' + x + ', ' + y + ')');

	// Draw button rectangle
	btn1.append('rect').attr('width', w).attr('height', h).
		attr('rx', rx).attr('ry', ry).on('click', callback);
	
	// Draw button text
	btn1.append('text').attr('x', w/2).attr('y', h/2).attr('dy', 0.8).
		style('alignment-baseline', 'middle').style('text-anchor', 'middle').
		text(txt).call(textWrap, w);
} // end function drawTextButton(...)

// Taken from https://bl.ocks.org/mbostock/7555321
function textWrap(text, width) {
	text.each(function() {
		var text = d3.select(this),
			words = text.text().split(/\s+/).reverse(),
			word,
			line = [],
			lineNumber = 0,
			lineHeight = 1.1, // ems
			y = text.attr("y"),
			dy = parseFloat(text.attr("dy")),
			tspan = text.text(null).append("tspan").attr("x", width/2).attr("y", y).attr("dy", dy + "em");
		
		while (word = words.pop()) {
			line.push(word);
			tspan.text(line.join(" "));
			if (tspan.node().getComputedTextLength() > width) {
				line.pop();
				tspan.text(line.join(" "));
				line = [word];
				tspan = text.append("tspan").attr("x", width/2).attr("y", y).
					attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
			}
		}
		
		// Move the text-anchor of the resulting paragraph back to the text-anchor of the initial
		// one line text
		var em_in_px = getElementPropertyPx(text[0][0], 'fontSize');
		text.attr('transform', 'translate(0, ' + (-(lineNumber * lineHeight + dy)/2 * em_in_px) + ')');
	});
} // end function textWrap(...)

function getElementPropertyPx(elem, prop) {
	return Number(getComputedStyle(elem)[prop].match(/(\d*(\.\d*)?)px/)[1]);
} // end function getElementPropertyPx(...)
