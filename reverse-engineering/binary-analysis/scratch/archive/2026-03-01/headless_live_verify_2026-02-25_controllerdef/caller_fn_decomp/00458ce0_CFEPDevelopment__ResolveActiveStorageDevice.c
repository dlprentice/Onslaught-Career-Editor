/* address: 0x00458ce0 */
/* name: CFEPDevelopment__ResolveActiveStorageDevice */
/* signature: void __fastcall CFEPDevelopment__ResolveActiveStorageDevice(void * this, int force_refresh) */


void __fastcall CFEPDevelopment__ResolveActiveStorageDevice(void *this,int force_refresh)

{
  bool bVar1;
  int iVar2;
  void *unaff_ESI;
  int device;
  int local_10;
  int local_c;
  int local_8;
  int local_4;

  bVar1 = CMovieCamera__GetShowHUD(unaff_ESI);
  if (bVar1) {
    *(undefined4 *)((int)this + 0x14) = 1;
  }
  device = 0;
  if (*(int *)((int)this + 0x10) < 0) {
    local_10 = 0;
  }
  else {
    PCPlatform__GetStorageDeviceInfo
              (*(int *)((int)this + 0x10),&local_10,&local_4,(int *)0x0,(int *)0x0);
  }
  if ((*(int *)((int)this + 0x10) == -1) && (iVar2 = VFuncSlot_09_005019c0(), iVar2 != 0)) {
    return;
  }
  if (local_10 != 0) {
    return;
  }
  iVar2 = VFuncSlot_09_005019c0();
  if (iVar2 == 0) {
    iVar2 = -1;
    PCPlatform__GetStorageDeviceCount(&local_c);
    if (0 < local_c) {
      do {
        if (iVar2 != -1) goto LAB_00458dad;
        PCPlatform__GetStorageDeviceInfo(device,&local_8,(int *)0x0,(int *)0x0,(int *)0x0);
        if (local_8 != 0) {
          iVar2 = device;
        }
        device = device + 1;
      } while (device < local_c);
      if (iVar2 != -1) {
LAB_00458dad:
        *(int *)((int)this + 8) = iVar2;
        *(undefined4 *)((int)this + 0xc) = 1;
        *(int *)((int)this + 0x10) = iVar2;
        goto LAB_00458dcb;
      }
    }
    *(undefined4 *)((int)this + 8) = 0xffffffff;
    *(undefined4 *)((int)this + 0xc) = 0xffffffff;
    *(undefined4 *)((int)this + 0x10) = 0xfffffffe;
  }
  else {
    *(undefined4 *)((int)this + 8) = 0;
    *(undefined4 *)((int)this + 0xc) = 0;
    *(undefined4 *)((int)this + 0x10) = 0xffffffff;
  }
LAB_00458dcb:
  if (((DAT_00677614 != 0) && (3 < DAT_00677624)) && ((DAT_00677624 < 7 || (DAT_00677624 == 9)))) {
    DAT_00677614 = 0;
  }
  return;
}
