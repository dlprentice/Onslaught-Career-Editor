/* address: 0x0059e0b0 */
/* name: CDXTexture__WriteJpegMarkerByte */
/* signature: void __stdcall CDXTexture__WriteJpegMarkerByte(int param_1) */


void CDXTexture__WriteJpegMarkerByte(int param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined1 *puVar3;
  int *piVar4;
  int iVar5;
  int *unaff_ESI;

  puVar2 = (undefined4 *)unaff_ESI[6];
  puVar3 = (undefined1 *)*puVar2;
  *puVar3 = 0xff;
  *puVar2 = puVar3 + 1;
  piVar1 = puVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if (*piVar1 == 0) {
    iVar5 = (*(code *)puVar2[3])();
    if (iVar5 == 0) {
      puVar2 = (undefined4 *)*unaff_ESI;
      puVar2[5] = 0x18;
      (*(code *)*puVar2)();
    }
  }
  piVar4 = (int *)unaff_ESI[6];
  puVar3 = (undefined1 *)*piVar4;
  *puVar3 = (undefined1)param_1;
  *piVar4 = (int)(puVar3 + 1);
  piVar1 = piVar4 + 1;
  *piVar1 = *piVar1 + -1;
  if (*piVar1 == 0) {
    iVar5 = (*(code *)piVar4[3])();
    if (iVar5 == 0) {
      puVar2 = (undefined4 *)*unaff_ESI;
      puVar2[5] = 0x18;
                    /* WARNING: Could not recover jumptable at 0x0059e0fc. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (*(code *)*puVar2)();
      return;
    }
  }
  return;
}
