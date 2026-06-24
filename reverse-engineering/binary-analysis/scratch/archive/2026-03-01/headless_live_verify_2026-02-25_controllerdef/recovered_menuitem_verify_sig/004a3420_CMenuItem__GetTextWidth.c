/* address: 0x004a3420 */
/* name: CMenuItem__GetTextWidth */
/* signature: int __thiscall CMenuItem__GetTextWidth(void * this) */


int __thiscall CMenuItem__GetTextWidth(void *this)

{
  short *text;
  void *this_00;
  int *out_extent_xy;
  int aiStack_8 [2];

  out_extent_xy = aiStack_8;
  text = (short *)(**(code **)(*(int *)this + 8))();
  this_00 = CPlatform__Font(&DAT_0088a0a8,1);
  CDXFont__GetTextExtent(this_00,text,out_extent_xy);
  return aiStack_8[0];
}
