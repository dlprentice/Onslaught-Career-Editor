/* address: 0x005d0820 */
/* name: CDXTexture__Helper_005d0820 */
/* signature: int __cdecl CDXTexture__Helper_005d0820(void * param_1, int param_2, int param_3) */


int __cdecl CDXTexture__Helper_005d0820(void *param_1,int param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  undefined4 *puVar3;

  if (((*(uint *)((int)param_1 + 0xc) & 0x83) == 0) ||
     (((param_3 != 0 && (param_3 != 1)) && (param_3 != 2)))) {
    puVar3 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar3 = 0x16;
    iVar2 = -1;
  }
  else {
    *(uint *)((int)param_1 + 0xc) = *(uint *)((int)param_1 + 0xc) & 0xffffffef;
    if (param_3 == 1) {
      iVar2 = CRT__FTellAdjusted(param_1);
      param_2 = param_2 + iVar2;
      param_3 = 0;
    }
    CDXTexture__FlushWriteStreamSegment(param_1);
    uVar1 = *(uint *)((int)param_1 + 0xc);
    if ((uVar1 & 0x80) == 0) {
      if ((((uVar1 & 1) != 0) && ((uVar1 & 8) != 0)) && ((uVar1 & 0x400) == 0)) {
        *(undefined4 *)((int)param_1 + 0x18) = 0x200;
      }
    }
    else {
      *(uint *)((int)param_1 + 0xc) = uVar1 & 0xfffffffc;
    }
    iVar2 = CRT__LseekFd(*(uint *)((int)param_1 + 0x10),param_2,param_3);
    iVar2 = (iVar2 != -1) - 1;
  }
  return iVar2;
}
