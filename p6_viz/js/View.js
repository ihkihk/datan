function View() {
	// A d3-selected SVG primitve that can be used as a canvas (e.g. <g>)
	this.d3c = null;
	
	// Size of the view in user units (width, height)
	this.size = {h: null, w: null};
	
	// Controller of the view
	this.ctrl = null;
	
	// Function for creating the view
	this.create = function() {
		console.log("WARNING! Non-overridden function 'create' called for View: " + this);
	};
	
	// Function for showing or hiding the view
	this.show = function(flShow, flAnim=true)
	{
		var state = flShow ? 'block' : 'none';
		var animDuration = flAnim ? 100 : 0;
		
		this.d3c.transition().attr('display', state);
	};	
	
}