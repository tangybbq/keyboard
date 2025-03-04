# The Jolt 3

The Jolt 2, with the varying-elevation design has turned out to be a rather nice keyboard to use.
However there are some challenges:

- Even with sockets, assembling all of the key risers is quite time consuming.  This makes it more
  challenging to experiment with the rest of the electronics.
- With more circuitry on the main board, the left/right distinction greatly increases the work to
  try a new design.

As such, the main goal of the Jolt 3 is to modularize the board design.  This is similar to using
existing rp2040 modules in the design, but in this case, the mezzanine board is my design instead,
with the following changes:

- Larger available area.  This allows me to put more on the board.
- Always have a debug headers.  The plethora of small boards that don't bother with debug headers is
  baffling to me.  I understand a lot of people are doing python, but this makes the board almost
  entirely useless for any serious development.

In order to make this board able to be used on either side of the keyboard, we'll need to avoid any
connectors that vary from side to side, notably the rj-45 (or whatever jack I decide on).  Now might
be a good time to try a different connector.  USB-C would work well for this, but it seems to be
hard to find thin USB-C cables.  I don't want 240W, I want a thin cable.  The old Apple cable is
really nice, but is getting harder and harder to find.  Another option is RJ-9.  The cables aren't
quite as available (and tend to be curly), but this might be a nice compromise.

Another thought, since I now have a tented stand, is to put the rj45 on the bottom side of the
board, and cut a notch for it.

It is fine to have the USB and debug header on the small board.

Sockets are going to be nice.  Regular pin header sockets are fine, but do lift the board up quite a
bit.  It still might end up being the best approach, as narrower pitch are harder to find.

This design should make some number of pins available in standard places:

- GPIOs for row and column.  4+6 is adequate for any of my current designs.  A two-row version with
  a single CPU would need 5+6, so 11 pins for this seems fine.
- Pins for the RJ-45?  If this is underneath, it gives more space.
- Battery.  The base board should be designed to allow a battery underneath.  The lines will just
  run directly to the small board.

## Dimensions

If we put the RJ-45 underneath, this gives us 41mm across by 39mm high.  It might make more sense to
just have the board be square at 40x40mm.

For a two-row design, this space could still be available.  It is unclear to me where my future
desire for 2-row will go (it depends on whether I become fully comfortable with steno+taipo).

## Design

The main boards will be jolt3-left, and jolt3-right, with the same connector on each.

- Supports the 7 risers in the same positioning and connection as the jolt2.
- Has a 40x40mm area for a mezzanine board.
- Defines a pinout for connections between the boards.  There are 20 pins needed, plus whatever is
  needed for extra grounding. A single row is likely to be fine.r
- Decide on the particular mezzanine connector to use.  It might make sense to have on one side with
  standoffs on the other sides.

The smallest M-2 size is 22x42, which would fit (but give half the available area.

I've ended up going for the [DF40C](https://www.hirose.com/product/p/CL0684-4010-9-51#) series of
connectors, 30 pin with a 3mm board spacing.  I could probably do 2mm, but the pins on the RJ-45 are
fairly long, and 3mm avoids the need to trim.  I'll use 3 1mm thick nylon washers for each standoff.

Rev A implements the following:

- jolt3-left: The left side.  The only components are the holes to mount the risers, the RJ-45, a
  place to mount the 2AA battery holder, and two pull up resistors for I2C.
- jolt3-right: The same as left, with minor changes: no pullups on I2C, Tx and Rx on the serial
  lines are swapped.
- jolt3-mez2040: The rp2040 circuitry on the mezzanine board.  I ended up with 38x38mm, to bring the
  mounting holes in enough on the main board to clear the stand.  The rp2040 is rotated 90 degrees
  to better route gpios to the connector (moves the crystal out of the way).
- Use the same riser boards "jolt2-verts" from the Jolt2.

The biggest change from previous designs is moving away from the Arm Cortex-M debug header to the
6-pin [Tag Connect](https://www.tag-connect.com/).  This requires no components on the board, just
some holes and pads, taking about the same area as the Cortex-M connector.  There is a smaller one,
but for these prototypes, the definitive connection seems better.  The cable is about $45 and should
last a long time.
