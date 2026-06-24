/* address: 0x005af5f0 */
/* name: CDXTexture__Helper_005af5f0 */
/* signature: void __thiscall CDXTexture__Helper_005af5f0(void * this, int param_1, void * param_2, int param_3, void * param_4) */


void __thiscall
CDXTexture__Helper_005af5f0(void *this,int param_1,void *param_2,int param_3,void *param_4)

{
  int iVar1;
  void *extraout_ECX;
  int iVar2;

  if (0x10 < *(uint *)((int)param_2 + 0x28)) {
    iVar2 = 0;
    if (0 < *(int *)(param_1 + 0x13c)) {
      do {
        if ((*(byte *)(param_3 + iVar2 * 4) & 7) != 0) {
          iVar1 = *(int *)param_1;
          *(undefined4 *)(iVar1 + 0x14) = 2;
          (**(code **)(iVar1 + 4))(param_1,0xffffffff);
          this = extraout_ECX;
          break;
        }
        iVar2 = iVar2 + 1;
      } while (iVar2 < *(int *)(param_1 + 0x13c));
    }
    if ((iVar2 == *(int *)(param_1 + 0x13c)) &&
       ((*(int *)(param_1 + 0x48) == 5 || (*(int *)(param_1 + 0x48) == 6)))) {
      CDXTexture__ConvertYccBlocksToRgb_Sse((int)this,(int)param_2,param_1,(void *)param_3);
      return;
    }
  }
  CDXTexture__Helper_005aee40((void *)param_1,(int)param_2,(void *)param_3);
  return;
}
