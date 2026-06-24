/* address: 0x004a43a0 */
/* name: CMenuItem__ButtonPressed */
/* signature: void __thiscall CMenuItem__ButtonPressed(void * this, int from_controller, int button) */


void __thiscall CMenuItem__ButtonPressed(void *this,int from_controller,int button)

{
  bool bVar1;
  int iVar2;

  bVar1 = false;
  if (button == 0x2c) {
    if (*(int **)((int)this + 0x34) != (int *)0x0) {
      (**(code **)(**(int **)((int)this + 0x34) + 0x18))(this);
    }
    *(undefined4 *)((int)this + 0x28) = *(undefined4 *)((int)this + 0x24);
  }
  else if (button == 0x36) {
    iVar2 = *(int *)((int)this + 0x24) + -1;
    *(int *)((int)this + 0x24) = iVar2;
    if (iVar2 < 0) {
      *(undefined4 *)((int)this + 0x24) = 0;
      bVar1 = true;
    }
    else {
      (**(code **)(*(int *)this + 0x38))();
      CFrontEnd__PlaySound(0);
      bVar1 = true;
    }
  }
  else if (button == 0x37) {
    iVar2 = *(int *)((int)this + 0x24) + 1;
    *(int *)((int)this + 0x24) = iVar2;
    if (*(int *)((int)this + 0x2c) < iVar2) {
      *(int *)((int)this + 0x24) = *(int *)((int)this + 0x2c);
      bVar1 = true;
    }
    else {
      (**(code **)(*(int *)this + 0x38))();
      CFrontEnd__PlaySound(0);
      bVar1 = true;
    }
  }
  if ((*(char *)((int)this + 0x30) != '\0') && (bVar1)) {
    if (*(int **)((int)this + 0x34) != (int *)0x0) {
      (**(code **)(**(int **)((int)this + 0x34) + 0x18))(this);
    }
    *(undefined4 *)((int)this + 0x28) = *(undefined4 *)((int)this + 0x24);
  }
  return;
}
