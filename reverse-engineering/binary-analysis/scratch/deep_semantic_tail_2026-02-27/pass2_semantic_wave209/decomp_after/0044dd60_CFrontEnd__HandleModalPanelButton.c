/* address: 0x0044dd60 */
/* name: CFrontEnd__HandleModalPanelButton */
/* signature: void __thiscall CFrontEnd__HandleModalPanelButton(void * this, int param_1, int param_2) */


void __thiscall CFrontEnd__HandleModalPanelButton(void *this,int param_1,int param_2)

{
  if ((*(int *)((int)this + 0x1f80) == 1) && (*(int *)((int)this + 0x1f8c) != 0)) {
    switch(*(undefined4 *)((int)this + 0x1f98)) {
    case 1:
      if (param_1 == 0x2c) {
        CFrontEnd__PlaySound(1);
        if (*(int *)((int)this + 0x1fa8) != -2) {
          CFrontEnd__SetPage(&DAT_0089d758,*(int *)((int)this + 0x1fa8),*(int *)((int)this + 0x1fac)
                            );
        }
LAB_0044ddd4:
        *(undefined4 *)((int)this + 0x1f7c) = 0;
        *(undefined4 *)((int)this + 0x1f80) = 2;
        *(undefined4 *)((int)this + 0x1fa8) = 0xfffffffe;
        return;
      }
      break;
    case 2:
      if (param_1 == 0x2a) {
        CFrontEnd__PlaySound(0);
        if (*(int *)((int)this + 0x1fa0) != 1) {
          *(undefined4 *)((int)this + 0x1fa0) = 1;
        }
      }
      else if (param_1 == 0x2b) {
        CFrontEnd__PlaySound(0);
        if (*(int *)((int)this + 0x1fa0) != 0) {
          *(undefined4 *)((int)this + 0x1fa0) = 0;
          return;
        }
      }
      else if (param_1 == 0x2c) {
        CFrontEnd__PlaySound(1);
        *(undefined4 *)((int)this + 0x1fa4) = *(undefined4 *)((int)this + 0x1fa0);
        goto LAB_0044ddd4;
      }
      break;
    case 3:
    case 4:
      if (param_1 == 0x2c) {
        CFrontEnd__PlaySound(1);
        if (*(int *)((int)this + 0x1fa8) != -2) {
          CFrontEnd__SetPage(&DAT_0089d758,*(int *)((int)this + 0x1fa8),*(int *)((int)this + 0x1fac)
                            );
        }
        *(undefined4 *)((int)this + 0x1fa4) = 1;
        goto LAB_0044ddd4;
      }
    }
  }
  return;
}
