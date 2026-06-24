/* address: 0x004a4290 */
/* name: CMenuItemSlider__ButtonPressed */
/* signature: void __thiscall CMenuItemSlider__ButtonPressed(void * this, int from_controller, int button) */


void __thiscall CMenuItemSlider__ButtonPressed(void *this,int from_controller,int button)

{
  undefined4 *puVar1;
  int *piVar2;

  if (button == 0x2c) {
    DAT_00704868 = DAT_00704868 + 1;
    puVar1 = *(undefined4 **)(*(int *)((int)this + 0x1c) + 8);
    *(undefined4 **)(*(int *)((int)this + 0x1c) + 0x10) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
    while (piVar2 != (int *)0x0) {
      (**(code **)(*piVar2 + 0x2c))();
      puVar1 = *(undefined4 **)(*(int *)(*(int *)((int)this + 0x1c) + 0x10) + 4);
      *(undefined4 **)(*(int *)((int)this + 0x1c) + 0x10) = puVar1;
      if (puVar1 == (undefined4 *)0x0) {
        piVar2 = (int *)0x0;
      }
      else {
        piVar2 = (int *)*puVar1;
      }
    }
  }
  return;
}
