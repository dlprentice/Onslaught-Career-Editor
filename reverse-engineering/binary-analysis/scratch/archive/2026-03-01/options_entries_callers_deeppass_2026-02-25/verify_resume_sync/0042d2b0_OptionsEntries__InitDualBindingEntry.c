/* address: 0x0042d2b0 */
/* name: OptionsEntries__InitDualBindingEntry */
/* signature: void * __thiscall OptionsEntries__InitDualBindingEntry(void * this, byte active, int entry_id, int slot0_device_code, short slot0_scan, int slot1_device_code, short slot1_scan, short slot0_vk, short slot1_vk) */


void * __thiscall
OptionsEntries__InitDualBindingEntry
          (void *this,byte active,int entry_id,int slot0_device_code,short slot0_scan,
          int slot1_device_code,short slot1_scan,short slot0_vk,short slot1_vk)

{
  *(int *)((int)this + 4) = entry_id;
  *(byte *)this = active;
  *(int *)((int)this + 0xc) = slot0_device_code;
  *(undefined4 *)((int)this + 8) = 0;
  *(short *)((int)this + 0x10) = slot0_scan;
  *(undefined4 *)((int)this + 0x14) = 0;
  *(short *)((int)this + 0x12) = slot0_vk;
  *(int *)((int)this + 0x18) = slot1_device_code;
  *(short *)((int)this + 0x1c) = slot1_scan;
  *(short *)((int)this + 0x1e) = slot1_vk;
  return this;
}
