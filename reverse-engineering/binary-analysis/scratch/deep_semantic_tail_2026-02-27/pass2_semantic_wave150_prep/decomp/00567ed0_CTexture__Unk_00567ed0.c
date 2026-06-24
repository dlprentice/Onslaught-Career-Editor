/* address: 0x00567ed0 */
/* name: CTexture__Unk_00567ed0 */
/* signature: int CTexture__Unk_00567ed0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_00567ed0(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int in_stack_00000004;
  int in_stack_00000008;
  int in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;
  int in_stack_0000001c;
  undefined1 local_28 [16];
  int local_18;
  uint local_14;
  int local_c;

  uVar2 = in_stack_00000004 - 0x76c;
  if (((int)uVar2 < 0x46) || (0x8a < (int)uVar2)) {
    iVar1 = -1;
  }
  else {
    iVar3 = *(int *)(&DAT_00656a6c + in_stack_00000008 * 4) + in_stack_0000000c;
    if (((uVar2 & 3) == 0) && (2 < in_stack_00000008)) {
      iVar3 = iVar3 + 1;
    }
    CRT__EnsureTzsetInitialized();
    local_18 = in_stack_00000008 + -1;
    iVar1 = ((in_stack_00000010 + (uVar2 * 0x16d + iVar3 + (in_stack_00000004 + -0x76d >> 2)) * 0x18
             ) * 0x3c + in_stack_00000014) * 0x3c + DAT_00656988 + 0x7c558180 + in_stack_00000018;
    if ((in_stack_0000001c == 1) ||
       (((in_stack_0000001c == -1 && (DAT_0065698c != 0)) &&
        (local_14 = uVar2, local_c = iVar3, iVar3 = CRT__IsInDst_WrapperLocked((int)local_28),
        iVar3 != 0)))) {
      iVar1 = iVar1 + _DAT_00656990;
    }
  }
  return iVar1;
}
