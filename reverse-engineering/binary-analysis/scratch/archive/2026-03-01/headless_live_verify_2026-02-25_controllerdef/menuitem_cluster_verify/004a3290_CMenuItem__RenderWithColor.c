/* address: 0x004a3290 */
/* name: CMenuItem__RenderWithColor */
/* signature: undefined CMenuItem__RenderWithColor(void) */


void __thiscall
CMenuItem__RenderWithColor
          (int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  undefined4 uVar1;

  uVar1 = (**(code **)(*param_1 + 8))();
  CMenuItem__Render(param_2,param_3,param_4,param_5,uVar1);
  return;
}
