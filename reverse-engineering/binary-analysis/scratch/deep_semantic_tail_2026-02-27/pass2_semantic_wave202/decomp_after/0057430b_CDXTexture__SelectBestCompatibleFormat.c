/* address: 0x0057430b */
/* name: CDXTexture__SelectBestCompatibleFormat */
/* signature: int __stdcall CDXTexture__SelectBestCompatibleFormat(void * param_1, int param_2, void * param_3) */


int CDXTexture__SelectBestCompatibleFormat(void *param_1,int param_2,void *param_3)

{
  int *piVar1;
  uint uVar2;
  uint uVar3;
  int *piVar4;

  uVar3 = 0xffffffff;
  piVar4 = &DAT_005e6a40;
  do {
    if (*(int *)param_1 == 0) {
      return *piVar4;
    }
    piVar1 = CDXTexture__FindFormatDescriptorById(*(int *)param_1);
    if ((*piVar1 != 0) && ((piVar1[1] != 1 || (param_2 != 0)))) {
      if (*(int *)param_3 == *piVar1) {
        return *(int *)param_3;
      }
      uVar2 = CFastVB__ComputeFormatMatchPenalty((int)param_3,(int)piVar1);
      if (((uVar2 != 0xffffffff) && (uVar2 <= uVar3)) &&
         ((uVar2 != uVar3 || ((uint)piVar1[2] < (uint)piVar4[2])))) {
        uVar3 = uVar2;
        piVar4 = piVar1;
      }
    }
    param_1 = (void *)((int)param_1 + 4);
  } while( true );
}
