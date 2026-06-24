/* address: 0x00453f50 */
/* name: Controls__DispatchRemap */
/* signature: void __cdecl Controls__DispatchRemap(int action_code, int key_or_value, void * callback) */


/* Dispatch helper for control remapping.
   Maps action_code (0x3B..0x4C) to one or more (entry_id, binding_type) pairs and invokes
   callback(key_or_value, entry_id, binding_type).
   These entry_id/binding_type pairs correspond to 0x20-byte persisted options entries in
   defaultoptions.bea / .bes options block. */

void __cdecl Controls__DispatchRemap(int action_code,int key_or_value,void *callback)

{
  switch(action_code) {
  case 0x3b:
    (*callback)(key_or_value,0x1f,9);
    return;
  case 0x3c:
    (*callback)(key_or_value,0x20,9);
    return;
  case 0x3d:
    (*callback)(key_or_value,0x1d,9);
    return;
  case 0x3e:
    (*callback)(key_or_value,0x1e,9);
    return;
  case 0x40:
    (*callback)(key_or_value,0x1a,9);
    return;
  case 0x41:
    (*callback)(key_or_value,0x1c,9);
    return;
  case 0x42:
    (*callback)(key_or_value,0x19,9);
    return;
  case 0x43:
    (*callback)(key_or_value,0x1b,9);
    return;
  case 0x45:
    (*callback)(key_or_value,0x10,9);
    return;
  case 0x46:
    (*callback)(key_or_value,0x11,9);
    return;
  case 0x48:
    (*callback)(key_or_value,0x12,10);
    (*callback)(key_or_value,0x13,9);
    return;
  case 0x49:
    (*callback)(key_or_value,0x14,10);
    return;
  case 0x4a:
    (*callback)(key_or_value,0x21,8);
    return;
  case 0x4b:
    (*callback)(key_or_value,0x15,9);
    return;
  case 0x4c:
    (*callback)(key_or_value,0x3b,8);
  }
  return;
}
