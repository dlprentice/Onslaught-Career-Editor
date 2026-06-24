/* address: 0x0052b760 */
/* name: CD3DApplication__Unk_0052b760 */
/* signature: int __fastcall CD3DApplication__Unk_0052b760(void * param_1) */


int __fastcall CD3DApplication__Unk_0052b760(void *param_1)

{
  int iVar1;
  DWORD DVar2;
  int *piVar3;
  int iStack_c;

  iStack_c = 0x52b769;
  iVar1 = (**(code **)(*(int *)param_1 + 0x14))();
  if (-1 < iVar1) {
    iStack_c = (int)param_1 + 0x32e58;
    iVar1 = (**(code **)(**(int **)((int)param_1 + 0x32ea0) + 0x40))
                      (*(int **)((int)param_1 + 0x32ea0));
    if (-1 < iVar1) {
      piVar3 = (int *)0x0;
      (**(code **)(**(int **)((int)param_1 + 0x32ea0) + 0x48))
                (*(int **)((int)param_1 + 0x32ea0),0,0,0,&iStack_c);
      (**(code **)(*piVar3 + 0x30))(piVar3);
      (**(code **)(*(int *)((int)param_1 + 0x32fd4) + 8))((int *)((int)param_1 + 0x32fd4));
      if ((*(int *)((int)param_1 + 0x330c4) != 0) && (*(int *)((int)param_1 + 0x32e44) == 0)) {
        DVar2 = GetClassLongA(*(HWND *)((int)param_1 + 0x32e94),-0xc);
        CD3DApplication__Unk_0052c8d0(*(void **)((int)param_1 + 0x32ea0),DVar2);
        (**(code **)(**(int **)((int)param_1 + 0x32ea0) + 0x30))
                  (*(int **)((int)param_1 + 0x32ea0),1);
      }
      iVar1 = (**(code **)(*(int *)param_1 + 0x24))();
      if (-1 < iVar1) {
        if (*(int *)((int)param_1 + 0x32e50) == 0) {
          *(undefined4 *)((int)param_1 + 0x32e54) = 1;
          CD3DApplication__Helper_0052cd20(1);
          CD3DApplication__Helper_0052cd20(2);
        }
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}
