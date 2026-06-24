/* address: 0x004a4450 */
/* name: FUN_004a4450 */
/* signature: undefined FUN_004a4450(void) */


int __fastcall FUN_004a4450(int *param_1)

{
  short *text;
  void *this;
  int *out_extent_xy;
  int aiStack_8 [2];

  out_extent_xy = aiStack_8;
  text = (short *)(**(code **)(*param_1 + 8))();
  this = CPlatform__Font(&DAT_0088a0a8,1);
  CDXFont__GetTextExtent(this,text,out_extent_xy);
  return aiStack_8[0] + 0x6a;
}
