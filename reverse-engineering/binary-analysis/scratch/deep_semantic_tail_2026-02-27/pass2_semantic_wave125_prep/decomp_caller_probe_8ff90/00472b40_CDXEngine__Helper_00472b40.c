/* address: 0x00472b40 */
/* name: CDXEngine__Helper_00472b40 */
/* signature: void __thiscall CDXEngine__Helper_00472b40(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CDXEngine__Helper_00472b40(void *this,int param_1,void *param_2)

{
  int iVar1;
  float unaff_EDI;
  bool bVar2;

  if (*(char *)((int)this + 0x1c) != '\0') {
    if (*(int *)((int)this + 0x44) == 1) {
      if (*(int *)((int)this + 0x20) == 0) {
        CController__RelinquishControl((void *)param_1);
        CGame__UnPause(&DAT_008a9a98);
        bVar2 = *(char *)((int)this + 0x1c) == '\0';
        *(bool *)((int)this + 0x1c) = bVar2;
        if (bVar2) {
          *(undefined4 *)((int)this + 0x20) = 0;
          iVar1 = *(int *)((int)this + 0x2c);
          while ((iVar1 == 0 && (*(int *)((int)this + 0x20) < 6))) {
            iVar1 = *(int *)((int)this + 0x20) + 1;
            *(int *)((int)this + 0x20) = iVar1;
            iVar1 = *(int *)((int)this + iVar1 * 4 + 0x2c);
          }
          *(undefined1 *)((int)this + 0x14) = 0;
          PlatformInput__ShutdownMouse();
        }
        else {
          PlatformInput__InitMouse();
        }
      }
      if (*(int *)((int)this + 0x20) == 1) {
        bVar2 = *(char *)((int)this + 0x1c) == '\0';
        *(bool *)((int)this + 0x1c) = bVar2;
        if (bVar2) {
          *(undefined4 *)((int)this + 0x20) = 0;
          iVar1 = *(int *)((int)this + 0x2c);
          while ((iVar1 == 0 && (*(int *)((int)this + 0x20) < 6))) {
            iVar1 = *(int *)((int)this + 0x20) + 1;
            *(int *)((int)this + 0x20) = iVar1;
            iVar1 = *(int *)((int)this + iVar1 * 4 + 0x2c);
          }
          *(undefined1 *)((int)this + 0x14) = 0;
          PlatformInput__ShutdownMouse();
        }
        else {
          PlatformInput__InitMouse();
        }
        CController__SetToControl((void *)param_1,DAT_008a9d88);
        CMessageLog__ResetRenderState((int)DAT_008a9d88);
      }
      if (*(int *)((int)this + 0x20) == 2) {
        bVar2 = *(char *)((int)this + 0x1c) == '\0';
        *(bool *)((int)this + 0x1c) = bVar2;
        if (bVar2) {
          *(undefined4 *)((int)this + 0x20) = 0;
          iVar1 = *(int *)((int)this + 0x2c);
          while ((iVar1 == 0 && (*(int *)((int)this + 0x20) < 6))) {
            iVar1 = *(int *)((int)this + 0x20) + 1;
            *(int *)((int)this + 0x20) = iVar1;
            iVar1 = *(int *)((int)this + iVar1 * 4 + 0x2c);
          }
          *(undefined1 *)((int)this + 0x14) = 0;
          PlatformInput__ShutdownMouse();
        }
        else {
          PlatformInput__InitMouse();
        }
        CController__SetToControl((void *)param_1,DAT_008a9d94);
        CExplosionInitThing__Unk_0048ff90((int)DAT_008a9d94);
      }
      if (*(int *)((int)this + 0x20) == 3) {
        CFrontEnd__PlaySound(1);
        _DAT_008a9acc = 4;
        if (DAT_008a9ac0 < 4) {
          DAT_008a9ac0 = 9;
        }
      }
      if (*(int *)((int)this + 0x20) == 4) {
        CFrontEnd__PlaySound(1);
        _DAT_008a9acc = 6;
        if (DAT_008a9ac0 < 4) {
          DAT_008a9ac0 = 9;
        }
      }
      if (*(int *)((int)this + 0x20) == 5) {
        *(undefined4 *)((int)this + 0x44) = 2;
        *(undefined4 *)((int)this + 0x20) = 0;
        return;
      }
    }
    if (*(int *)((int)this + 0x44) == 2) {
      if (*(int *)((int)this + 0x20) == 0) {
        CEngine__Unk_004d3020
                  (DAT_008a9d3c,(uint)(*(int *)((int)DAT_008a9d3c + 0x20) == 0),unaff_EDI);
      }
      if (*(int *)((int)this + 0x20) == 1) {
        if (DAT_008a9ab8 == 1) {
          DAT_008a9ab8 = 0;
        }
        else if (*(int *)((int)DAT_008a9d3c + 0x28) != 2) {
          DAT_008a9ab8 = 1;
        }
      }
      if (*(int *)((int)this + 0x20) == 2) {
        *(undefined4 *)((int)this + 0x44) = 1;
        *(undefined4 *)((int)this + 0x20) = 0;
      }
    }
  }
  return;
}
