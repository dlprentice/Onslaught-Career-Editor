/* address: 0x004659a0 */
/* name: CDXEngine__Helper_004659a0 */
/* signature: int CDXEngine__Helper_004659a0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXEngine__Helper_004659a0(void)

{
  int iVar1;
  float in_stack_00000004;
  float in_stack_00000008;
  uint in_stack_0000000c;
  undefined4 in_stack_00000010;
  undefined4 in_stack_00000014;
  undefined4 in_stack_00000018;
  undefined4 in_stack_0000001c;
  undefined4 in_stack_00000020;

  CDXFont__DrawTextScaled
            (in_stack_00000004 + _DAT_005d8568,in_stack_00000008 + _DAT_005d8568,in_stack_00000018,
             in_stack_0000001c,in_stack_00000020,in_stack_0000000c & 0xff000000,in_stack_00000010,
             in_stack_00000014,0);
  iVar1 = CDXFont__DrawTextScaled
                    (in_stack_00000004,in_stack_00000008,in_stack_00000018,in_stack_0000001c,
                     in_stack_00000020,in_stack_0000000c,in_stack_00000010,in_stack_00000014,0);
  return iVar1;
}
