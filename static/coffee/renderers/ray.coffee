
properties = require('./properties')
glyph_properties = properties.glyph_properties
line_properties = properties.line_properties

glyph = require('./glyph')
Glyph = glyph.Glyph
GlyphView = glyph.GlyphView


class RayView extends GlyphView

  initialize: (options) ->
    glyphspec = @mget('glyphspec')
    @glyph_props = new glyph_properties(
      @,
      glyphspec,
      ['x', 'y', 'angle', 'length'],
      [
        new line_properties(@, glyphspec)
      ]
    )

    @do_stroke = @glyph_props.line_properties.do_stroke
    super(options)

  _render: (data) ->
    ctx = @plot_view.ctx
    glyph_props = @glyph_props

    ctx.save()

    width = @plot_view.viewstate.get('width')
    height = @plot_view.viewstate.get('height')
    inf_len = 2 * (width + height)

    x = (glyph_props.select('x', obj) for obj in data)
    y = (glyph_props.select('y', obj) for obj in data)
    [@sx, @sy] = @map_to_screen(x, glyph_props.x.units, y, glyph_props.y.units)
    @angle = (glyph_props.select('angle', obj) for obj in data) # TODO deg/rad
    @length = (glyph_props.select('length', obj) for obj in data)
    for i in [0..@sx.length-1]
      if @length[i] == 0 then @length[i] = inf_len

    if @glyph_props.fast_path
      @_fast_path(ctx, glyph_props)
    else
      @_full_path(ctx, glyph_props, data)

    ctx.restore()

  _fast_path: (ctx, glyph_props) ->
    if @do_stroke
      glyph_props.line_properties.set(ctx, glyph)
      ctx.beginPath()
      for i in [0..@sx.length-1]
        if isNaN(@sx[i] + @sy[i] + @angle[i] + @length[i])
          continue

        ctx.translate(@sx[i], @sy[i])
        ctx.rotate(@angle[i])
        ctx.moveTo(0,  0)
        ctx.lineTo(@length[i], 0) # TODO handle @length in data units?
        ctx.rotate(-@angle[i])
        ctx.translate(-@sx[i], -@sy[i])

      ctx.stroke()

  _full_path: (ctx, glyph_props, data) ->
    if @do_stroke
      for i in [0..@sx.length-1]
        if isNaN(@sx[i] + @sy[i] + @angle[i] + @length[i])
          continue

        ctx.translate(@sx[i], @sy[i])
        ctx.rotate(@angle[i])

        ctx.beginPath()
        ctx.moveTo(0, 0)
        ctx.lineTo(@length[i], 0) # TODO handle @length in data units?

        glyph_props.line_properties.set(ctx, data[i])
        ctx.stroke()

        ctx.rotate(-@angle[i])
        ctx.translate(-@sx[i], -@sy[i])


class Ray extends Glyph
  default_view: RayView
  type: 'GlyphRenderer'


Ray::display_defaults = _.clone(Ray::display_defaults)
_.extend(Ray::display_defaults, {

  line_color: 'red'
  line_width: 1
  line_alpha: 1.0
  line_join: 'miter'
  line_cap: 'butt'
  line_dash: []

})

class Rays extends Backbone.Collection
  model: Ray

exports.rays = new Rays
exports.Ray = Ray
exports.RayView = RayView

