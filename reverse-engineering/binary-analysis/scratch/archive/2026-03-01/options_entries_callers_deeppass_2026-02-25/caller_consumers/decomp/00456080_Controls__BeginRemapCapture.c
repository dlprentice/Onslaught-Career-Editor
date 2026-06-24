/* address: 0x00456080 */
/* name: Controls__BeginRemapCapture */
/* signature: undefined Controls__BeginRemapCapture(void) */


void __fastcall Controls__BeginRemapCapture(int param_1)

{
  int *piVar1;
  int iVar2;
  float *pfVar3;
  int iVar4;
  float10 fVar5;

  iVar2 = *(int *)(param_1 + 0x28) + 0x37;
  if (iVar2 == 0x38) {
    (&CAREER_mInvertYWalker_P1)[*(int *)(param_1 + 0x24)] =
         (uint)((&CAREER_mInvertYWalker_P1)[*(int *)(param_1 + 0x24)] == 0);
    return;
  }
  if (iVar2 != 0x39) {
    iVar4 = 0;
    g_ControlRemapActive = 0;
    g_ControlRemapArmed = 0;
    if (0 < DAT_00888ff8) {
      pfVar3 = (float *)&DAT_00677810;
      do {
        piVar1 = DAT_008a9564;
        if (DAT_008a9564 == (int *)0x0) {
          piVar1 = CGame__GetController(&DAT_008a9a98,0);
        }
        fVar5 = (float10)(**(code **)(*piVar1 + 0x24))(iVar4);
        pfVar3[-2] = (float)fVar5;
        fVar5 = (float10)(**(code **)(*piVar1 + 0x28))(iVar4);
        pfVar3[-1] = (float)fVar5;
        fVar5 = (float10)(**(code **)(*piVar1 + 0x2c))(iVar4);
        *pfVar3 = (float)fVar5;
        fVar5 = (float10)(**(code **)(*piVar1 + 0x30))(iVar4);
        pfVar3[1] = (float)fVar5;
        fVar5 = (float10)(**(code **)(*piVar1 + 0x34))(iVar4);
        pfVar3[2] = (float)fVar5;
        fVar5 = (float10)(**(code **)(*piVar1 + 0x38))(iVar4);
        pfVar3[3] = (float)fVar5;
        iVar4 = iVar4 + 1;
        pfVar3 = pfVar3 + 6;
      } while (iVar4 < DAT_00888ff8);
    }
    g_ControlRemapSlotIndex = *(undefined4 *)(param_1 + 0x24);
    g_ControlRemapVkScanPacked._0_2_ = 0;
    g_ControlRemapActionCode = iVar2;
    PLATFORM__SetKeySink(&LAB_00456190);
    return;
  }
  (&CAREER_mInvertYFlight_P1)[*(int *)(param_1 + 0x24)] =
       (uint)((&CAREER_mInvertYFlight_P1)[*(int *)(param_1 + 0x24)] == 0);
  return;
}
