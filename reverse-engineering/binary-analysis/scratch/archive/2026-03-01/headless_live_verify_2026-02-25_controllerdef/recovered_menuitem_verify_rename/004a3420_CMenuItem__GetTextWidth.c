/* address: 0x004a3420 */
/* name: CMenuItem__GetTextWidth */
/* signature: undefined CMenuItem__GetTextWidth(void) */


int __fastcall CMenuItem__GetTextWidth(int *param_1)

{
  short *text;
  void *this;
  int *out_extent_xy;
  int aiStack_8 [2];

  out_extent_xy = aiStack_8;
  text = (short *)(**(code **)(*param_1 + 8))();
  this = CPlatform__Font(&DAT_0088a0a8,1);
  CDXFont__GetTextExtent(this,text,out_extent_xy);
  return aiStack_8[0];
}
