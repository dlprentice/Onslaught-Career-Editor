/* address: 0x005202d0 */
/* name: CFEPVirtualKeyboard__Process */
/* signature: void __thiscall CFEPVirtualKeyboard__Process(void * this, int state) */


void __thiscall CFEPVirtualKeyboard__Process(void *this,int state)

{
  int iVar1;

  iVar1 = state;
  if (state != 3) {
    CFEPDirectory__RefreshSaveFileList(&DAT_008a1f8c,state);
  }
  if (iVar1 == 0) {
    if (DAT_00889008 != &DAT_0051feb0) {
      PlatformInput__SetKeySinkCore(&DAT_00855bb0,&DAT_0051feb0);
    }
    if (DAT_00677614 == 0) {
      CMovieCamera__GetShowHUD(this);
      PCPlatform__GetStorageDeviceInfo
                (DAT_008a9694,&state,(int *)&stack0xfffffffc,(int *)0x0,(int *)0x0);
      if (state == 0) {
        CFEPLoadGame__Helper_00464b30(0x3c);
        return;
      }
    }
  }
  else if (DAT_00889008 == &DAT_0051feb0) {
    PlatformInput__SetKeySinkCore(&DAT_00855bb0,(void *)0x0);
  }
  return;
}
