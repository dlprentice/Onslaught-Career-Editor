/* address: 0x0042d260 */
/* name: OptionsEntries__InitSingleBindingEntry */
/* signature: void * __thiscall OptionsEntries__InitSingleBindingEntry(void * this, byte active, int entry_id, int slot0_device_code, short slot0_scan, short slot0_vk) */


void * __thiscall
OptionsEntries__InitSingleBindingEntry
          (void *this,byte active,int entry_id,int slot0_device_code,short slot0_scan,short slot0_vk
          )

{
  *(int *)((int)this + 4) = entry_id;
  *(int *)((int)this + 0xc) = slot0_device_code;
  *(byte *)this = active;
  *(short *)((int)this + 0x10) = slot0_scan;
  *(undefined4 *)((int)this + 8) = 0;
  *(short *)((int)this + 0x12) = slot0_vk;
  *(undefined4 *)((int)this + 0x14) = 0xffffffff;
  *(undefined4 *)((int)this + 0x18) = 0;
  *(undefined2 *)((int)this + 0x1c) = 0;
  *(undefined2 *)((int)this + 0x1e) = 0;
  return this;
}
