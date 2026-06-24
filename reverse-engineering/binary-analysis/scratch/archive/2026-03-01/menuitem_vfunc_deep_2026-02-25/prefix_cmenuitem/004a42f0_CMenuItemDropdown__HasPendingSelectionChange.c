/* address: 0x004a42f0 */
/* name: CMenuItemDropdown__HasPendingSelectionChange */
/* signature: bool __thiscall CMenuItemDropdown__HasPendingSelectionChange(void * this) */


bool __thiscall CMenuItemDropdown__HasPendingSelectionChange(void *this)

{
  if ((*(char *)((int)this + 0x25) != '\0') &&
     (*(int *)((int)this + 0x1c) != *(int *)((int)this + 0x20))) {
    return true;
  }
  return false;
}
