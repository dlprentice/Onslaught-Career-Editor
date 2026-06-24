/* address: 0x004d05c0 */
/* name: CMenuItemRange__IsBindingActive */
/* signature: int __thiscall CMenuItemRange__IsBindingActive(void * this) */


int __thiscall CMenuItemRange__IsBindingActive(void *this)

{
  if ((*(int *)((int)this + 8) != 0) && (*(char *)(*(int *)((int)this + 8) + 8) != '\0')) {
    return 1;
  }
  return 0;
}
