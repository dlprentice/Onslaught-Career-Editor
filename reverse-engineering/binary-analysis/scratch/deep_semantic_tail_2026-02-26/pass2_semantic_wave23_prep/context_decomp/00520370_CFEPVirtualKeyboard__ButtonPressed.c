/* address: 0x00520370 */
/* name: CFEPVirtualKeyboard__ButtonPressed */
/* signature: void __thiscall CFEPVirtualKeyboard__ButtonPressed(void * this, int button, float val) */


void __thiscall CFEPVirtualKeyboard__ButtonPressed(void *this,int button,float val)

{
  short sVar1;
  int iVar2;
  int iVar3;
  void *unaff_ESI;

  switch(button) {
  case 0x2a:
    break;
  case 0x2b:
    if (*(int *)((int)this + 0x6e8) != 4) {
      CFEPVirtualKeyboard__Unk_00520f70(this,*(int *)((int)this + 0x6e8) + 1,(float)unaff_ESI);
      return;
    }
    CFEPVirtualKeyboard__Unk_00520f70(this,0,(float)unaff_ESI);
    return;
  case 0x2c:
    CFrontEnd__PlaySound(1);
    iVar2 = *(int *)((int)this + 0x6e4) * 5 + *(int *)((int)this + 0x6e8);
    CFEPVirtualKeyboard__Unk_00520cc0
              (this,CONCAT22((short)((uint)(iVar2 * 7) >> 0x10),
                             *(undefined2 *)
                              ((int)this + (*(int *)((int)this + 0x6ec) + iVar2 * 0xe) * 8 + 0x54)),
               unaff_ESI);
    return;
  default:
    return;
  case 0x2e:
    CFrontEnd__PlaySound(2);
    CFrontEnd__SetPage(&DAT_0089d758,0,0x46);
    return;
  case 0x36:
    *(undefined4 *)((int)this + 0x6f4) = 0x3f000000;
    do {
      if (*(int *)((int)this + 0x6ec) == 0) {
        iVar2 = *(int *)((int)this + 0x6e4) * 5 + *(int *)((int)this + 0x6e8);
        sVar1 = *(short *)((int)this + iVar2 * 0x70 + 0x5c);
        while (sVar1 != 0) {
          iVar3 = *(int *)((int)this + 0x6ec) + 1;
          *(int *)((int)this + 0x6ec) = iVar3;
          sVar1 = *(short *)((int)this + (iVar3 + iVar2 * 0xe) * 8 + 0x5c);
        }
      }
      else {
        *(int *)((int)this + 0x6ec) = *(int *)((int)this + 0x6ec) + -1;
      }
      iVar2 = CFEPVirtualKeyboard__Helper_005214d0((int)this);
    } while (iVar2 != 0);
    return;
  case 0x37:
    *(undefined4 *)((int)this + 0x6f4) = 0x3f000000;
    do {
      if (*(short *)((int)this +
                    (*(int *)((int)this + 0x6ec) +
                    (*(int *)((int)this + 0x6e4) * 5 + *(int *)((int)this + 0x6e8)) * 0xe) * 8 +
                    0x5c) == 0) {
        *(undefined4 *)((int)this + 0x6ec) = 0;
      }
      else {
        *(int *)((int)this + 0x6ec) = *(int *)((int)this + 0x6ec) + 1;
      }
      iVar2 = CFEPVirtualKeyboard__Helper_005214d0((int)this);
    } while (iVar2 != 0);
    return;
  }
  if (*(int *)((int)this + 0x6e8) != 0) {
    CFEPVirtualKeyboard__Unk_00520f70(this,*(int *)((int)this + 0x6e8) + -1,(float)unaff_ESI);
    return;
  }
  CFEPVirtualKeyboard__Unk_00520f70(this,4,(float)unaff_ESI);
  return;
}
