/* address: 0x004b24d0 */
/* name: CMeshPart__Unk_004b24d0 */
/* signature: int __thiscall CMeshPart__Unk_004b24d0(void * this, int param_1, float param_2, float param_3, void * param_4, void * param_5) */


int __thiscall
CMeshPart__Unk_004b24d0
          (void *this,int param_1,float param_2,float param_3,void *param_4,void *param_5)

{
  int iVar1;
  double dVar2;
  int iStack_8;

  if (((*(int *)(*(int *)((int)this + 0x128) + 0x14) != 0) && (1 < *(int *)((int)this + 0xb8))) &&
     (-1 < (int)param_2)) {
    iVar1 = *(int *)(*(int *)((int)this + 0x128) + 0x18);
    param_2 = (float)*(int *)(iVar1 + (int)param_2 * 0x24 + 0x14) +
              (float)*(int *)(iVar1 + 0x1c + (int)param_2 * 0x24) * (float)param_1;
    if (param_4 != (void *)0x0) {
      (**(code **)(*(int *)param_4 + 0x14))(this,&param_2);
    }
    dVar2 = CDXEngine__Helper_0055dfe7((double)param_2);
    iStack_8 = (int)(longlong)ROUND(dVar2);
    iVar1 = *(int *)((int)this + 0xb8);
    dVar2 = CDXEngine__Helper_0055dfe7((double)param_2);
    *(float *)param_3 = param_2 - (float)dVar2;
    return iStack_8 % iVar1;
  }
  param_1 = 0;
  if (param_4 != (void *)0x0) {
    (**(code **)(*(int *)param_4 + 0x14))(this,&param_1);
  }
  dVar2 = CDXEngine__Helper_0055dfe7((double)(float)param_1);
  iStack_8 = (int)(longlong)ROUND(dVar2);
  dVar2 = CDXEngine__Helper_0055dfe7((double)(float)param_1);
  *(float *)param_3 = (float)param_1 - (float)dVar2;
  return iStack_8;
}
