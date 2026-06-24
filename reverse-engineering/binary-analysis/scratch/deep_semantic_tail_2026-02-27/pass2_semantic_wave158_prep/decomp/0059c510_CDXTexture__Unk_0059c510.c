/* address: 0x0059c510 */
/* name: CDXTexture__Unk_0059c510 */
/* signature: void __stdcall CDXTexture__Unk_0059c510(void * param_1) */


void CDXTexture__Unk_0059c510(void *param_1)

{
  int iVar1;
  undefined4 *extraout_EAX;
  undefined4 *puVar2;
  int unaff_EDI;

  *(undefined4 *)((int)param_1 + 4) = 0;
  iVar1 = CDXTexture__Unk_005b1da0();
  CDXTexture__Unk_005b1c00((int)param_1,0x54);
  if (extraout_EAX == (undefined4 *)0x0) {
    CFrontEndPage__Process_NoOp(param_1,unaff_EDI);
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x36;
    puVar2[6] = 0;
    (*(code *)*puVar2)(param_1);
  }
  *extraout_EAX = CDXTexture__AllocFromBank_SplitBlock;
  extraout_EAX[1] = CDXTexture__AllocLinearBlockAndTrack;
  extraout_EAX[2] = CDXTexture__AllocRowPointerTableAndRows;
  extraout_EAX[3] = CDXTexture__AllocMcuRowPointerTableAndRows;
  extraout_EAX[4] = CDXTexture__CreateDecodeJobDescriptor;
  extraout_EAX[5] = CDXTexture__Helper_0059be70;
  extraout_EAX[6] = &LAB_0059bee0;
  extraout_EAX[7] = &LAB_0059c1b0;
  extraout_EAX[8] = &LAB_0059c2d0;
  extraout_EAX[9] = CDXTexture__Unk_0059c3f0;
  extraout_EAX[10] = &LAB_0059c4d0;
  extraout_EAX[0xc] = 1000000000;
  extraout_EAX[0xb] = iVar1;
  puVar2 = extraout_EAX + 0x10;
  iVar1 = 2;
  do {
    puVar2[-2] = 0;
    *puVar2 = 0;
    puVar2 = puVar2 + -1;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  *(undefined4 **)((int)param_1 + 4) = extraout_EAX;
  extraout_EAX[0x11] = 0;
  extraout_EAX[0x12] = 0;
  extraout_EAX[0x13] = 0x54;
  return;
}
