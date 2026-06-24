/* address: 0x0059ef60 */
/* name: CDXTexture__WriteJpegQuantTablesAndFrame */
/* signature: void __stdcall CDXTexture__WriteJpegQuantTablesAndFrame(void * param_1) */


void CDXTexture__WriteJpegQuantTablesAndFrame(void *param_1)

{
  bool bVar1;
  char cVar2;
  undefined3 extraout_var;
  int *piVar3;
  int iVar4;
  int iVar5;

  iVar4 = 0;
  iVar5 = 0;
  if (0 < *(int *)((int)param_1 + 0x3c)) {
    piVar3 = (int *)(*(int *)((int)param_1 + 0x44) + 0x10);
    do {
      cVar2 = CDXTexture__WriteJpegQuantTable(*piVar3);
      iVar4 = iVar4 + CONCAT31(extraout_var,cVar2);
      iVar5 = iVar5 + 1;
      piVar3 = piVar3 + 0x15;
    } while (iVar5 < *(int *)((int)param_1 + 0x3c));
  }
  if (((*(int *)((int)param_1 + 0xb4) == 0) && (*(int *)((int)param_1 + 0xec) == 0)) &&
     (*(int *)((int)param_1 + 0x38) == 8)) {
    iVar5 = *(int *)((int)param_1 + 0x3c);
    bVar1 = true;
    if (0 < iVar5) {
      piVar3 = (int *)(*(int *)((int)param_1 + 0x44) + 0x18);
      do {
        if ((1 < piVar3[-1]) || (1 < *piVar3)) {
          bVar1 = false;
        }
        piVar3 = piVar3 + 0x15;
        iVar5 = iVar5 + -1;
      } while (iVar5 != 0);
    }
    if ((iVar4 != 0) && (bVar1)) {
      iVar4 = *(int *)param_1;
      *(undefined4 *)(iVar4 + 0x14) = 0x4b;
      (**(code **)(iVar4 + 4))(param_1,0);
    }
  }
  if (*(int *)((int)param_1 + 0xb4) == 0) {
    if (*(int *)((int)param_1 + 0xec) == 0) {
      CDXTexture__WriteJpegFrameHeader(param_1);
      return;
    }
    CDXTexture__WriteJpegFrameHeader(param_1);
    return;
  }
  CDXTexture__WriteJpegFrameHeader(param_1);
  return;
}
