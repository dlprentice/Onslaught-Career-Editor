/* address: 0x0048f2f0 */
/* name: CDXLandscape__Helper_0048f2f0 */
/* signature: int CDXLandscape__Helper_0048f2f0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXLandscape__Helper_0048f2f0(void)

{
  int extraout_EAX;
  int in_ECX;
  undefined4 in_stack_00000004;
  undefined4 in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;

  *(undefined4 *)(in_ECX + 0x4c) = in_stack_00000010;
  *(undefined4 *)(in_ECX + 0x2c) = in_stack_00000004;
  *(undefined4 *)(in_ECX + 0x30) = in_stack_00000008;
  *(undefined4 *)(in_ECX + 0x34) = in_stack_0000000c;
  CLandscapeVB__RebuildHeightGridVertexBuffer(in_ECX);
  return extraout_EAX;
}
