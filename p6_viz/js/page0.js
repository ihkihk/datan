
var page0View = new View();

page0View.create = function(d3c, ctrl, flShow)
{
		this.d3c = d3c.append('g').attr('class', 'story-page0');
		this.ctrl = ctrl;

		/*this.d3c.append('rect').attr('class', 'shadow').attr('transform', 'translate(3,3)').attr('x', 0).attr('y', 0).attr('width', 800).attr('height', 500).
			attr('rx', 5); */
		this.d3c.append('rect').attr('x', 0).attr('y', 0).attr('width', 1200).attr('height', 650).
			attr('rx', 5);
		this.d3c.append('text').attr('transform', 'translate(50,100)').text('Page0');
		
		this.show(flShow, false);
}; // end function create(...)

var page0Ctrl = {
	view : page0View,
	parentCtrl: null,
	pageShown:null,
	
	createView: function(d3c, parentCtrl, flShow) {
		this.parentCtrl = parentCtrl;
		this.view.create(d3c, this, flShow);
		this.pageShown = flShow;
	},
	
	show: function(flShow)
	{
		this.pageShown = flShow;
		this.view.show(flShow);
	}
};
