/*******************************************************************************
 * File:        drawPrimitives.js
 * Project:     DATAN P6
 * Purpose:     Auxiliary functions used by the SVG viz engine
 * Author:      Ivailo Kassamakov (c) 2016
 * Created:     15-Jul-2016  
 * Last change: 
 * Notes:       
 ******************************************************************************/
 
"use strict";

////////////////////////////////////////////////////////////////////////////////
// Draw SVG clickable button with a centered & wrapped text inside.
//
// Inputs:
//    parent   - A d3-selected object to contain the button
//    x, y     - number: SVG coordinates in user space (i.e. px) of the upper right corner
//    w, h     - number: SVG lengths (width, height) in user space (i.e. px)
//    txt      - string: Text to be contained by the button (without newlines!)
//    cls      - string: a CSS class name for the button
//    id       - string: an HTML ID attribute for the button
//    callback - function to call when the button is clicked
//    rx, ry   - number: SVG lengths (border rounding radius) in user space (i.e. px)
// Output:
//    None
// Notes:
//    The text inside of the button will be automatically wrapped.
//    The button can be styled by CSS-selecting ".<cls> rect" and ".<cls> text"
////////////////////////////////////////////////////////////////////////////////
function drawTextButton(parent, x, y, w, h, txt, cls, id, callback, rx=20, ry=30) {
	// Create a group to contain both the rect and text elements
	var btn1 = parent.append('g').attr('class', cls).attr('id', id).
		attr('transform', 'translate(' + x + ', ' + y + ')');

	// Draw button rectangle
	btn1.append('rect').attr('width', w).attr('height', h).
		attr('rx', rx).attr('ry', ry).on('click', callback);
	
	// Draw button text
	btn1.append('text').attr('x', w/2).attr('y', h/2).attr('dy', 0.8).
		style('alignment-baseline', 'middle').style('text-anchor', 'middle').
		text(txt).call(textWrap, w);
} // end function drawTextButton(...)

////////////////////////////////////////////////////////////////////////////////
// Wrap a text string to fit in a given width.
//
// Input:
//    text  - A d3-selection of one or more SVG text elements
//    width - number: SVG length in user space (i.e. px) specifying the max
//            width of the resulting text paragraph
// Output:
//    None
// Notes:
//    Adapted from https://bl.ocks.org/mbostock/7555321
//    The split lines will create "tspan" elements inside of the original "text" element.
//    The split lines will inherit the alignment of the parent "text" element.
//    The resulting paragraph will be centered vertically around the "text-anchor" of
//        the original "text" element.
////////////////////////////////////////////////////////////////////////////////
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
			tspan = text.text(null).append("tspan").attr("x", width/2).
				attr("y", y).attr("dy", dy + "em");
		
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
		var em_in_px = getElementPropertyPx(text.nodes()[0], 'fontSize');
		text.attr('transform', 'translate(0, ' + (-(lineNumber * lineHeight + dy)/2 * em_in_px) + ')');
	});
} // end function textWrap(...)

////////////////////////////////////////////////////////////////////////////////
// Return a CSS property of a given element that is measured in px.
//
// Input:
//    elem - an Element (e.g. SVGElement or HTMLElement, etc.) to query
//    prop - string: The name of the CSS property (e.g. 'width', 'fontSize', etc.)
// Output:
//    Number: the numeric value of the queried property
// Note:
//    Only properties that are in px units are supported, i.e. getComputedStyle()
//        will return strings like "15px" for them.
////////////////////////////////////////////////////////////////////////////////
function getElementPropertyPx(elem, prop) {
	return Number(getComputedStyle(elem)[prop].match(/(\d*(\.\d*)?)px/)[1]);
} // end function getElementPropertyPx(...)

/* EOF */