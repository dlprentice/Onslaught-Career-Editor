/* address: 0x0059f050 */
/* name: CDXTexture__Helper_0059f050 */
/* signature: void __stdcall CDXTexture__Helper_0059f050(void * param_1) */


void CDXTexture__Helper_0059f050(void *param_1)

{
  int iVar1;
  int iVar2;
  int unaff_EBX;
  int *piVar3;
  int iVar4;
  void *pvVar5;

  iVar1 = *(int *)((int)param_1 + 0x164);
  if ((*(int *)((int)param_1 + 0xb4) == 0) && (iVar4 = 0, 0 < *(int *)((int)param_1 + 0xfc))) {
    piVar3 = (int *)((int)param_1 + 0x100);
    do {
      iVar2 = *piVar3;
      if (*(int *)((int)param_1 + 0xec) == 0) {
        CDXTexture__WriteJpegHuffmanTable(param_1,*(void **)(iVar2 + 0x14),unaff_EBX);
        pvVar5 = *(void **)(iVar2 + 0x18);
LAB_0059f0c4:
        CDXTexture__WriteJpegHuffmanTable(param_1,pvVar5,unaff_EBX);
      }
      else {
        if (*(int *)((int)param_1 + 0x144) != 0) {
          pvVar5 = *(void **)(iVar2 + 0x18);
          goto LAB_0059f0c4;
        }
        if (*(int *)((int)param_1 + 0x14c) == 0) {
          pvVar5 = *(void **)(iVar2 + 0x14);
          goto LAB_0059f0c4;
        }
      }
      iVar4 = iVar4 + 1;
      piVar3 = piVar3 + 1;
    } while (iVar4 < *(int *)((int)param_1 + 0xfc));
  }
  if (*(int *)((int)param_1 + 200) != *(int *)(iVar1 + 0x1c)) {
    CDXTexture__WriteJpegRestartIntervalMarker();
    *(undefined4 *)(iVar1 + 0x1c) = *(undefined4 *)((int)param_1 + 200);
  }
  CDXTexture__WriteJpegScanHeader();
  return;
}
