/* address: 0x004a3260 */
/* name: CMenuItem__RenderCentered */
/* signature: undefined CMenuItem__RenderCentered(void) */


void __thiscall
CMenuItem__RenderCentered(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;

  uVar1 = (**(code **)(*param_1 + 8))();
  CMenuItem__Render(param_2,param_3,param_4,0xffffffff,uVar1);
  return;
}
