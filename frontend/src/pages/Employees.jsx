import { useState, useEffect } from 'react'
import { Users, Plus, Trash2, Pencil, Search, Mail, Phone, Briefcase } from 'lucide-react'
import { employeeAPI } from '../services/api'
import toast from 'react-hot-toast'
import { useGreeting } from '../hooks/useGreeting'
import Modal from '../components/ui/Modal'
import EmptyState from '../components/ui/EmptyState'
import { PageLoader } from '../components/ui/Spinner'
import EmployeeForm from '../components/employees/EmployeeForm'

export default function Employees() {
  const { greeting } = useGreeting()
  const [employees,    setEmployees]    = useState([])
  const [loading,      setLoading]      = useState(true)
  const [search,       setSearch]       = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [editEmployee, setEditEmployee] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const getButtonColor = () => {
    if (greeting.includes('Morning')) return 'rgb(143, 154, 179)'
    if (greeting.includes('Afternoon')) return 'rgb(91, 102, 129)'
    if (greeting.includes('Evening')) return 'rgb(49, 59, 82)'
    return 'rgb(143, 154, 179)'
  }

  const fetchEmployees = async () => {
    setLoading(true)
    try {
      const res = await employeeAPI.getAll()
      setEmployees(res.data)
    } catch {
      toast.error('Failed to load employees')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchEmployees() }, [])

  const handleDelete = async () => {
    setDeleteLoading(true)
    try {
      await employeeAPI.delete(deleteTarget.id)
      toast.success(`${deleteTarget.full_name} deleted`)
      setDeleteTarget(null)
      fetchEmployees()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Delete failed')
    } finally {
      setDeleteLoading(false)
    }
  }

  // Client-side search filter
  const filtered = employees.filter(e =>
    e.full_name.toLowerCase().includes(search.toLowerCase())   ||
    e.employee_id.toLowerCase().includes(search.toLowerCase()) ||
    e.department.toLowerCase().includes(search.toLowerCase())  ||
    e.email.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) return <PageLoader />

  return (
    <div className="p-6 space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
          <p className="text-sm text-gray-500 mt-0.5">{employees.length} total employees</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-all duration-150 hover:opacity-90"
          style={{ backgroundColor: getButtonColor() }}
        >
          <Plus size={16} /> Add Employee
        </button>
      </div>

      {/* Search bar */}
      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by name, ID, department..."
          className="input-field pl-9"
        />
      </div>

      {/* Empty state or table */}
      {filtered.length === 0 ? (
        <div className="card">
          <EmptyState
            icon={Users}
            title={search ? 'No results found' : 'No employees yet'}
            description={search ? 'Try a different search term' : 'Add your first employee to get started'}
            action={!search && (
              <button onClick={() => setShowAddModal(true)} className="btn-primary">
                <Plus size={16} /> Add Employee
              </button>
            )}
          />
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50/50">
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-5 py-3.5">Employee</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-5 py-3.5">Contact</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-5 py-3.5">Department</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-5 py-3.5">Position</th>
                  <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider px-5 py-3.5">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map(emp => (
                  <tr key={emp.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-semibold text-sm flex-shrink-0">
                          {emp.full_name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{emp.full_name}</p>
                          <p className="text-xs text-gray-400">{emp.employee_id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <p className="text-sm text-gray-700 flex items-center gap-1.5">
                        <Mail size={12} className="text-gray-400" /> {emp.email}
                      </p>
                      {emp.phone && (
                        <p className="text-sm text-gray-500 flex items-center gap-1.5 mt-0.5">
                          <Phone size={12} className="text-gray-400" /> {emp.phone}
                        </p>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-full">
                        <Briefcase size={11} /> {emp.department}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-sm text-gray-600">{emp.position || '—'}</span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setEditEmployee(emp)}
                          className="p-2 rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Edit"
                        >
                          <Pencil size={15} />
                        </button>
                        <button
                          onClick={() => setDeleteTarget(emp)}
                          className="p-2 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                          title="Delete"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Employee Modal */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add New Employee" size="lg">
        <EmployeeForm
          onSuccess={() => { setShowAddModal(false); fetchEmployees() }}
          onCancel={() => setShowAddModal(false)}
        />
      </Modal>

      {/* Edit Employee Modal */}
      <Modal isOpen={!!editEmployee} onClose={() => setEditEmployee(null)} title="Edit Employee" size="lg">
        <EmployeeForm
          employee={editEmployee}
          onSuccess={() => { setEditEmployee(null); fetchEmployees() }}
          onCancel={() => setEditEmployee(null)}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} title="Delete Employee">
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Are you sure you want to delete{' '}
            <span className="font-semibold text-gray-900">{deleteTarget?.full_name}</span>?
            This will also remove all their attendance records and cannot be undone.
          </p>
          <div className="flex justify-end gap-3">
            <button onClick={() => setDeleteTarget(null)} className="btn-secondary">Cancel</button>
            <button onClick={handleDelete} disabled={deleteLoading} className="btn-danger">
              {deleteLoading ? 'Deleting...' : 'Yes, Delete'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}