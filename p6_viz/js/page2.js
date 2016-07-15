var page2View = new View();

page2View.create = function(d3c, ctrl, flShow)
{
	this.d3c = d3c.append('g');
	this.ctrl = ctrl;

	this.d3c.attr('transform', 'translate(10,30)').append('text').text('Page2');
	
	this.show(flShow, false);

}; // end function create(...)

var page2Ctrl = {
	view : page2View,
	parentCtrl: null,
	
	createView: function(d3c, parentCtrl, flShow) {
		this.parentCtrl = parentCtrl;
		this.view.create(d3c, this, flShow);
	},

	show: function(flShow)
	{
		this.pageShown = flShow;
		this.view.show(flShow);
	}
};



