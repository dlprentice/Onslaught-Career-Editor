/* address: 0x004a4110 */
/* name: CMenuItemDropdown__ButtonPressed */
/* signature: void __thiscall CMenuItemDropdown__ButtonPressed(void * this, int from_controller, int button) */


void __thiscall CMenuItemDropdown__ButtonPressed(void *this,int from_controller,int button)

{
  byte bVar1;
  int iVar2;

  switch(button) {
  case 0x2a:
  case 0x36:
    CFrontEnd__PlaySound(0);
    iVar2 = *(int *)((int)this + 0x20) + -1;
    *(int *)((int)this + 0x20) = iVar2;
    if (iVar2 < 0) {
      *(undefined4 *)((int)this + 0x20) = 0;
    }
    *(undefined1 *)((int)this + 0x24) = 1;
    return;
  case 0x2b:
  case 0x37:
    CFrontEnd__PlaySound(0);
    *(int *)((int)this + 0x20) = *(int *)((int)this + 0x20) + 1;
    iVar2 = (**(code **)(*(int *)this + 0x40))();
    if (iVar2 <= *(int *)((int)this + 0x20)) {
      iVar2 = (**(code **)(*(int *)this + 0x40))();
      *(int *)((int)this + 0x20) = iVar2 + -1;
    }
    *(undefined1 *)((int)this + 0x24) = 1;
    return;
  case 0x2c:
    CFrontEnd__PlaySound(1);
    if ((*(char *)((int)this + 0x24) == '\0') &&
       (iVar2 = (**(code **)(*(int *)this + 0x40))(), iVar2 < 2)) {
      CFrontEnd__PlaySound(2);
      return;
    }
    bVar1 = *(byte *)((int)this + 0x24) ^ 1;
    *(byte *)((int)this + 0x24) = bVar1;
    if (((bVar1 == 0) && (*(char *)((int)this + 0x25) == '\0')) &&
       (iVar2 = *(int *)((int)this + 0x20), *(int *)((int)this + 0x1c) != iVar2)) {
      *(int *)((int)this + 0x1c) = iVar2;
      (**(code **)(*(int *)this + 0x38))(iVar2);
      return;
    }
    break;
  case 0x2e:
    if (*(char *)((int)this + 0x24) != '\0') {
      CFrontEnd__PlaySound(2);
      *(undefined1 *)((int)this + 0x24) = 0;
      *(undefined4 *)((int)this + 0x20) = *(undefined4 *)((int)this + 0x1c);
    }
  }
  return;
}
