var page1View = new View();

page1View.create = function(d3c, ctrl, flShow)
{
	this.d3c = d3c.append('g');
	this.ctrl = ctrl;

	this.d3c.attr('transform', 'translate(10,20)').append('text').text('Page1');
	
	this.show(flShow, false);

}; // end function create(...)

var page1Ctrl = {
	view : page1View,
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
