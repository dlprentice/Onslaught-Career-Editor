/* address: 0x0052bb80 */
/* name: CD3DApplication__Reset3DEnvironment */
/* signature: int __thiscall CD3DApplication__Reset3DEnvironment(void * this, void * param_1, int param_2, int param_3) */


int __thiscall CD3DApplication__Reset3DEnvironment(void *this,void *param_1,int param_2,int param_3)

{
  int iVar1;
  HMODULE hInstance;
  INT_PTR IVar2;
  LPCSTR lpTemplateName;
  HWND hWndParent;
  code *lpDialogFunc;
  void *dwInitParam;

  if (param_1 == (void *)0x0) {
    if ((*(int *)((int)this + 0x32e44) == 0) &&
       (iVar1 = CD3DApplication__Unk_0052b840(this), iVar1 < 0)) {
      CD3DApplication__Unk_0052c4f0(-0x7dfffff4);
      return -0x7fffbffb;
    }
    hWndParent = *(HWND *)((int)this + 0x32e94);
    lpDialogFunc = CD3DApplication__Unk_0052bc80;
    lpTemplateName = &DAT_00000090;
    dwInitParam = this;
    hInstance = GetModuleHandleA((LPCSTR)0x0);
    IVar2 = DialogBoxParamA(hInstance,lpTemplateName,hWndParent,lpDialogFunc,(LPARAM)dwInitParam);
    if (IVar2 != 1) {
      return 0;
    }
    *(undefined4 *)((int)this + 0x32e44) =
         *(undefined4 *)
          ((int)this +
          *(int *)((int)this + (*(int *)((int)this + 0x32e40) + 1) * 0x516c) * 0xf68 +
          *(int *)((int)this + 0x32e40) * 0x516c + 0x13b8);
  }
  (**(code **)(*(int *)this + 0x28))(param_2);
  iVar1 = CD3DApplication__Initialize3DEnvironment(1);
  if (-1 < iVar1) {
    if (*(int *)((int)this + 0x32e50) == 0) {
      *(undefined4 *)((int)this + 0x32e54) = 1;
      CD3DApplication__Helper_0052cd20(1);
      CD3DApplication__Helper_0052cd20(2);
    }
    return 0;
  }
  iVar1 = CD3DApplication__Unk_0052c4f0(iVar1);
  return iVar1;
}
