/* address: 0x00599406 */
/* name: CDXTexture__SerializeFloatGridChunk */
/* signature: int __stdcall CDXTexture__SerializeFloatGridChunk(void * param_1, void * param_2, void * param_3, void * param_4) */


int CDXTexture__SerializeFloatGridChunk(void *param_1,void *param_2,void *param_3,void *param_4)

{
  void *pvVar1;
  float *extraout_EAX;
  uint uVar2;
  void *pvVar3;
  int iVar4;
  float *pfVar5;
  undefined4 *local_8;

  iVar4 = 0;
  local_8 = (float *)0x0;
  pvVar3 = param_2;
  if (*(int *)((int)param_4 + 4) == 0xc) {
    pvVar3 = *(void **)((int)param_4 + 0x20);
  }
  if (*(int *)((int)pvVar3 + 4) == 1) {
    CFastVB__Helper_00426fd0((int)param_2 << 4);
    local_8 = extraout_EAX;
    if (extraout_EAX == (float *)0x0) {
      iVar4 = -0x7ff8fff2;
    }
    else {
      pfVar5 = extraout_EAX;
      for (uVar2 = (uint)((int)param_2 << 4) >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
        *pfVar5 = 0.0;
        pfVar5 = pfVar5 + 1;
      }
      for (iVar4 = 0; iVar4 != 0; iVar4 = iVar4 + -1) {
        *(undefined1 *)pfVar5 = 0;
        pfVar5 = (float *)((int)pfVar5 + 1);
      }
      if (param_2 != (void *)0x0) {
        param_4 = param_2;
        pvVar1 = param_3;
        pfVar5 = extraout_EAX;
        param_2 = extraout_EAX;
        do {
          for (; pvVar1 != (void *)0x0; pvVar1 = (void *)((int)pvVar1 + -1)) {
            iVar4 = *(int *)((int)pvVar3 + 8);
            if (*(int *)(iVar4 + 0x10) == 3) {
              *pfVar5 = (float)*(double *)(iVar4 + 0x18);
            }
            else {
              *pfVar5 = *(float *)(iVar4 + 0x18);
            }
            pvVar3 = *(void **)((int)pvVar3 + 0xc);
            pfVar5 = pfVar5 + 1;
          }
          pfVar5 = (float *)((int)param_2 + 0x10);
          param_4 = (void *)((int)param_4 + -1);
          pvVar1 = param_3;
          param_2 = pfVar5;
        } while (param_4 != (void *)0x0);
      }
      iVar4 = CDXTexture__RegisterSerializedChunk();
    }
  }
  OID__FreeObject_Callback(local_8);
  return iVar4;
}
