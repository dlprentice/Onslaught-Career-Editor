/* address: 0x005af570 */
/* name: CTexture__Helper_005af570 */
/* signature: void __stdcall CTexture__Helper_005af570(void * param_1, void * param_2, int param_3) */


void CTexture__Helper_005af570(void *param_1,void *param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int unaff_EDI;

  if (0x10 < *(uint *)((int)param_2 + 0x28)) {
    iVar2 = 0;
    if (0 < *(int *)((int)param_1 + 0x13c)) {
      do {
        if ((*(byte *)(param_3 + iVar2 * 4) & 7) != 0) {
          iVar1 = *(int *)param_1;
          *(undefined4 *)(iVar1 + 0x14) = 2;
          (**(code **)(iVar1 + 4))(param_1,0xffffffff);
          break;
        }
        iVar2 = iVar2 + 1;
      } while (iVar2 < *(int *)((int)param_1 + 0x13c));
    }
    if ((iVar2 == *(int *)((int)param_1 + 0x13c)) &&
       ((*(int *)((int)param_1 + 0x48) == 5 || (*(int *)((int)param_1 + 0x48) == 6)))) {
      CDXTexture__UpsampleAndConvertYccToRgb_Mmx(param_2,(int)param_1,param_3,unaff_EDI);
      return;
    }
  }
  CDXTexture__UpsampleChromaLinearHorizontal((int)param_1,(int)param_2,param_3);
  return;
}
